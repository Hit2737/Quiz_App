from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from quiz_app.auth import login_required, admin_login_required
from quiz_app.db import get_db
import json

bp = Blueprint('quiz', __name__)

@bp.route('/quiz/create', methods=('GET', 'POST'))
@admin_login_required
def create():
    if request.method == 'POST':
        quiz_id = request.form['quiz_id']
        quiz_name = request.form['quiz_name']
        session['quiz_id'] = quiz_id
        error = None

        if not quiz_id:
            error = 'Quiz ID is required.'
        elif not quiz_name:
            error = 'Quiz name is required.'

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'INSERT INTO Quizzes (quiz_id, quiz_name, admin_id)'
                ' VALUES (?, ?, ?)',
                (quiz_id, quiz_name, int(g.admin['admin_id']))
            )
            db.commit()
            return redirect(url_for('quiz.add_questions'))

    return render_template('create_quiz.html')

@bp.route('/add-questions', methods=['GET', 'POST'])
@admin_login_required
def add_questions():
    db = get_db()
    quiz_id = session.get('quiz_id')
    if not quiz_id:
        # Handle the case where quiz_id is not in session
        flash('Quiz ID is missing!', 'error')
        return redirect(url_for('quiz.dashboard'))

    quiz_data = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()
    
    if request.method == 'POST':
        print("POST request received")
        print(request.form)
        
        # Process the form data
        questions = []
        for key in request.form:
            print(f"{key}: {request.form[key]}")
            if key.startswith('question-'):
                questions.append({
                    'question': request.form[key],
                    'type': request.form.get(f'ques_type-{key.split("-")[1]}'),
                    'time_limit': {
                        'hours': request.form.get(f'hours-{key.split("-")[1]}'),
                        'minutes': request.form.get(f'minutes-{key.split("-")[1]}'),
                        'seconds': request.form.get(f'seconds-{key.split("-")[1]}')
                    },
                    'options': [
                        {
                            'text': request.form.get(f'option-{key.split("-")[1]}-{i+1}'),
                            'correct': request.form.get(f'correct-{key.split("-")[1]}-{i+1}') == 'on'
                        } for i in range(len([k for k in request.form if k.startswith(f'option-{key.split("-")[1]}')]))
                    ] if request.form.get(f'ques_type-{key.split("-")[1]}') == 'MCQ' else [],
                    'answer': request.form.get(f'answer-{key.split("-")[1]}') if request.form.get(f'ques_type-{key.split("-")[1]}') == 'Text' else None
                })
        
        print("Extracted questions:", questions)
        
        # Here you can save the questions to the database
        
        flash('Questions added successfully!', 'success')
    
    return render_template('add_ques.html', quiz_id=quiz_id, quiz_data=quiz_data)



@bp.route('/submit_response/<quiz_id>/<question_id>', methods=['POST'])
@login_required
def submit_response(quiz_id, question_id):
    db = get_db()
    user_id = g.user['id']
    selected_options = request.form.getlist('selected_option')
    print("Form Data:", request.form)  # Print the entire form data for debugging
    print("Selected Options:", selected_options)  # Print selected options
    selected_options_indices = [int(option) for option in selected_options] 
    selected_options_json = json.dumps(selected_options_indices)  # Convert the list to a JSON string
    print(selected_options_json)
    #checking if user has already attempted the question
    if db.execute(
        'SELECT * FROM UserResponses WHERE user_id = ? AND quiz_id = ? AND question_id = ?',
        (user_id, quiz_id, question_id)
    ).fetchone():
        return redirect(url_for('interface.dashboard'))
    else:
        db.execute(
            'INSERT INTO UserResponses (user_id, quiz_id, question_id, selected_options, time_stamp)'
            ' VALUES (?, ?, ?, ?, ?)', (user_id, quiz_id, question_id, selected_options_json, db.execute('SELECT DATETIME("now","localtime")').fetchone()[0])
        )
        db.commit()
    ques_count = db.execute(
        'SELECT COUNT(*) FROM Questions WHERE quiz_id = ?', (quiz_id,)
    ).fetchone()[0]
    if 'submit' in request.form:
        question_id = ques_count + 1
    elif 'submit_next' in request.form:
        question_id = int(question_id) + 1
    question_id = int(question_id) + 1
    session['current_question'] = question_id
    session['quiz_id'] = quiz_id
    return redirect(url_for('interface.quiz_interface'))

@bp.route('/quiz/start_time/<quiz_id>', methods=('GET', 'POST'))
@admin_login_required
def start_time(quiz_id):
    currenttime = get_db().execute('SELECT DATETIME("now","localtime")').fetchone()[0]
    currenttime = currenttime[:-2] + '00'
    print(currenttime)
    if request.method == 'POST':
        if 'manual' in request.form:
            return redirect(url_for('interface.admin_dashboard'))
        start_datetime = request.form['start_datetime']
        date,time = start_datetime.split('T')
        start_datetime = date + ' ' + time + ':00.000'  
        print(start_datetime)
        error = None
        if not start_datetime:
            error = 'Start date is required.'
        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                'UPDATE Quizzes SET start_time = ? WHERE quiz_id = ?',
                (start_datetime, quiz_id)
            )
            db.commit()
            return redirect(url_for('interface.admin_dashboard'))
        
    return render_template('start_time.html', quiz_id=quiz_id, currenttime=currenttime)

@bp.route('/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
@admin_login_required
def edit_quiz(quiz_id):
    db = get_db()
    quiz_data = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()
    # question_data = db.execute('SELECT * FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchone()
    if (quiz_data is None) or (quiz_data['admin_id'] != g.user['id']):
        abort(404)

    questions = db.execute('SELECT * FROM Questions WHERE quiz_id = ? ORDER BY question_id', (quiz_id,)).fetchall()
    questions_list = []
    for question in questions:
        question_dict = dict(question)
        question_dict['options'] = json.loads(question_dict['options'])
        question_dict['correct_options'] = json.loads(question_dict['correct_options'])
        questions_list.append(question_dict)
    if request.method == "POST":
        print("POST request received")
        if 'update' in request.form:
            print("Updating question")
            question_id = request.form['question_id']
            question_text = request.form['question']
            options = request.form['options']
            print("Options:", options)    
            hours = request.form['hours']
            minutes = request.form['minutes']
            seconds = request.form['seconds']
            if not hours and not minutes and not seconds:
                duration = None
            else:
                if not hours:
                    hours = '00'
                if not minutes:
                    minutes = '00'
                if not seconds:
                    seconds = '00'
                duration = hours + ':' + minutes + ':' + seconds + '.000'
            option_list = options.split(',')
            print("Options:", option_list)
            options_json = json.dumps(option_list)
            db.execute(
                'UPDATE Questions SET question_text = ?, options = ?, duration = ? WHERE quiz_id = ? AND question_id = ?',
                (question_text, options_json, duration, quiz_id, question_id)
            )
            db.commit()
            return redirect(url_for('quiz.edit_quiz', quiz_id=quiz_id, questions=questions_list))
    return render_template('edit_quiz.html', quiz_id=quiz_id, questions=questions_list)

    

    
@bp.route('/quiz/delete/<int:quiz_id>', methods=['GET','POST'])
@admin_login_required
def delete_quiz(quiz_id):
    db = get_db()
    print("Deleting quiz with id:", quiz_id)
    db.execute('DELETE FROM Quizzes WHERE quiz_id = ?', (quiz_id,))
    db.execute('DELETE FROM Questions WHERE quiz_id = ?', (quiz_id,))
    db.execute('DELETE FROM UserResponses WHERE quiz_id = ?', (quiz_id,))
    db.commit()
    return redirect(url_for('interface.admin_dashboard'))

@bp.route('/quiz/start/<int:quiz_id>', methods=['GET','POST'])
@admin_login_required
def start_quiz(quiz_id):
    db = get_db()
    db.execute('UPDATE Quizzes SET start_time = DATETIME("now","localtime") WHERE quiz_id = ?', (quiz_id,))
    db.commit()
    return redirect(url_for('quiz.lock_unlock_ques', quiz_id=quiz_id))

@bp.route('/quiz/lock_unlock_ques/<int:quiz_id>', methods=['GET','POST'])
@admin_login_required
def lock_unlock_ques(quiz_id):
    db = get_db()
    questions = db.execute('SELECT * FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchall()
    if request.method == 'POST':
        question_id = request.form['question_id']
        lock_unlock = db.execute('SELECT * FROM Questions WHERE quiz_id = ? AND question_id = ?', (quiz_id, question_id)).fetchone()['lock']
        lock_unlock = not lock_unlock
        print("Lock/Unlock:", lock_unlock)
        if 'lock_unlock' in request.form:
            db.execute('UPDATE Questions SET lock = ? WHERE quiz_id = ? AND question_id = ?', (lock_unlock ,quiz_id, question_id))
            db.commit()
        return redirect(url_for('quiz.lock_unlock_ques', quiz_id=quiz_id))
    return render_template('lock_unlock_ques.html', questions=questions, quiz_id=quiz_id)  

@bp.route('/quiz/forced_submit_quiz/<int:quiz_id>', methods=['GET','POST'])
@login_required
def forced_submit_quiz(quiz_id):
    db = get_db()
    db.execute('INSERT INTO UserResponses (user_id, quiz_id, question_id, selected_options) SELECT user_id, quiz_id, question_id, selected_options FROM UserResponses WHERE quiz_id = ?', (quiz_id,))
    return redirect(url_for('interface.dashboard'))