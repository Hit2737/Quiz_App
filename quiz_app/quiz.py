from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for, session
)
from werkzeug.exceptions import abort
from quiz_app.auth import login_required
from quiz_app.db import get_db
import json

bp = Blueprint('quiz', __name__)

@bp.route('/quiz/create', methods=('GET', 'POST'))
@login_required
def create():
    if request.method == 'POST':
        quiz_id = request.form['quiz_id']
        quiz_name = request.form['quiz_name']
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
                (quiz_id, quiz_name, int(g.user['id']))
            )
            db.commit()
            return redirect(url_for('quiz.add_questions',quiz_id=quiz_id))

    return render_template('create_quiz.html')

@bp.route('/add-questions/<quiz_id>', methods=('GET', 'POST'))
@login_required
def add_questions(quiz_id):
    db = get_db()
    quiz_data = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()
    if (quiz_data is None) or (quiz_data['admin_id'] != g.user['id']):
        abort(404)
    if request.method == 'POST':
        questions = request.form.getlist('question')
        hours = request.form.getlist('hours')
        minutes = request.form.getlist('minutes')
        seconds = request.form.getlist('seconds')
        print("Questions:", questions)
        for i in range(len(questions)):
            question = questions[i]
            option_list = request.form.getlist(f'options-{i}')
            correct_option_list = request.form.getlist(f'correct_options-{i}')
            correct_option_list = [int(option) for option in correct_option_list]
            # print("Form Data:", request.form)  # Print the entire form data for debugging
            # print("Form Data:", request.form.keys)  # Print the entire form data for debugging
            # print("Form Data:", request.form.values)  # Print the entire form data for debugging
            print("Options:", option_list)  # Print options
            print("Correct Options:", correct_option_list)

            hour = hours[i]
            minute = minutes[i]
            second = seconds[i]
            if not hour and not minute and not second:
                duration = None
            else:
                if not hour:
                    hour = '00'
                if not minute:
                    minute = '00'
                if not second:
                    second = '00'
                duration = f"{hour}:{minute}:{second}.000"

            if not question:
                flash('Question is required.')
            else:
                result = db.execute('SELECT MAX(question_id) FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchone()
                next_question_id = (result[0] or 0) + 1
                options_json = json.dumps(option_list)
                correct_options_json = json.dumps(correct_option_list)
                db.execute(
                    'INSERT INTO Questions (question_id, quiz_id, question_text, options, correct_options, duration)'
                    ' VALUES (?, ?, ?, ?, ?, ?)',
                    (next_question_id, quiz_id, question, options_json, correct_options_json, duration)
                )
                db.commit()

        if 'add_next' in request.form:
            return redirect(url_for('quiz.add_questions', quiz_id=quiz_id))
        else:
            return redirect(url_for('quiz.start_time', quiz_id=quiz_id))
    return render_template('addQues.html', quiz_id=quiz_id)


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
            'INSERT INTO UserResponses (user_id, quiz_id, question_id, selected_options)'
            ' VALUES (?, ?, ?, ?)',
            (user_id, quiz_id, question_id, selected_options_json)
        )
        db.commit()
    if 'submit_next' in request.form:
        question_id = int(question_id) + 1
    question_id = int(question_id) + 1
    session['current_question'] = question_id
    session['quiz_id'] = quiz_id
    return redirect(url_for('interface.student_interface'))

@bp.route('/quiz/start_time/<quiz_id>', methods=('GET', 'POST'))
@login_required
def start_time(quiz_id):
    currenttime = get_db().execute('SELECT DATETIME("now","localtime")').fetchone()[0]
    currenttime = currenttime[:-2] + '00'
    print(currenttime)
    if request.method == 'POST':
        if 'manual' in request.form:
            return redirect(url_for('interface.dashboard'))
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
            return redirect(url_for('interface.dashboard'))
        
    return render_template('start_time.html', quiz_id=quiz_id, currenttime=currenttime)

@bp.route('/quiz/edit_quiz/<int:quiz_id>', methods=['GET', 'POST'])
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
    if request.method == 'POST':
        delete_quiz_questions(quiz_id)
        questions = request.form.getlist('question')
        hours = request.form.getlist('hours')
        minutes = request.form.getlist('minutes')
        seconds = request.form.getlist('seconds')
        print("Questions:", questions)
        for i in range(len(questions)):
            question = questions[i]
            option_list = request.form.getlist(f'options-{i}')
            correct_option_list = request.form.getlist(f'correct_options-{i}')
            correct_option_list = [int(option) for option in correct_option_list]
            # print("Form Data:", request.form)  # Print the entire form data for debugging
            # print("Form Data:", request.form.keys)  # Print the entire form data for debugging
            # print("Form Data:", request.form.values)  # Print the entire form data for debugging
            print("Options:", option_list)  # Print options
            print("Correct Options:", correct_option_list)

            hour = hours[i]
            minute = minutes[i]
            second = seconds[i]
            if not hour and not minute and not second:
                duration = None
            else:
                if not hour:
                    hour = '00'
                if not minute:
                    minute = '00'
                if not second:
                    second = '00'
                duration = f"{hour}:{minute}:{second}.000"

            if not question:
                flash('Question is required.')
            else:
                result = db.execute('SELECT MAX(question_id) FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchone()
                next_question_id = (result[0] or 0) + 1
                options_json = json.dumps(option_list)
                correct_options_json = json.dumps(correct_option_list)
                db.execute(
                    'INSERT INTO Questions (question_id, quiz_id, question_text, options, correct_options, duration)'
                    ' VALUES (?, ?, ?, ?, ?, ?)',
                    (next_question_id, quiz_id, question, options_json, correct_options_json, duration)
                )
                db.commit()
        return redirect(url_for('interface.dashboard'))
    return render_template('edit_quiz.html', quiz_id=quiz_id, questions=questions_list)

    

    
@bp.route('/quiz/delete/<int:quiz_id>', methods=['GET','POST'])
def delete_quiz(quiz_id):
    db = get_db()
    print("Deleting quiz with id:", quiz_id)
    db.execute('DELETE FROM Quizzes WHERE quiz_id = ?', (quiz_id,))
    db.execute('DELETE FROM Questions WHERE quiz_id = ?', (quiz_id,))
    db.execute('DELETE FROM UserResponses WHERE quiz_id = ?', (quiz_id,))
    db.commit()
    return redirect(url_for('interface.dashboard'))

def delete_quiz_questions(quiz_id):
    db = get_db()
    db.execute('DELETE FROM Questions WHERE quiz_id = ?', (quiz_id,))
    db.commit()


@bp.route('/quiz/start/<int:quiz_id>', methods=['GET','POST'])
def start_quiz(quiz_id):
    db = get_db()
    db.execute('UPDATE Quizzes SET start_time = DATETIME("now","localtime") WHERE quiz_id = ?', (quiz_id,))
    db.commit()
    return redirect(url_for('quiz.lock_unlock_ques', quiz_id=quiz_id))

@bp.route('/quiz/lock_unlock_ques/<int:quiz_id>', methods=['GET','POST'])
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
