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
        question = request.form['question']
        options = request.form.getlist('options')
        correct_options = request.form.getlist('correct_options')

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
        print("Duration:", duration)
        if not question:
            flash('Question is required.')
        else:
            result= db.execute('SELECT MAX(question_id) FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchone()
            next_question_id= (result[0] or 0) + 1
            options_json = json.dumps(options)  # Convert the options list to a JSON string
            
            correct_indices = [index for index, value in enumerate(correct_options) if value == 'on']
            print(correct_options)
            # correct_indices = [int(index) for index in correct_options]
            correct_options_json = json.dumps(correct_indices) 
            print(correct_indices)
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

@bp.route('/quiz/edit/<int:quiz_id>', methods=['GET', 'POST'])
def edit_quiz(quiz_id):
    db = get_db()
    quiz_data = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()
    # question_data = db.execute('SELECT * FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchone()
    if (quiz_data is None) or (quiz_data['admin_id'] != g.user['id']):
        abort(404)


    questions = db.execute('SELECT * FROM Questions WHERE quiz_id = ? ORDER BY question_id', (quiz_id,)).fetchall()
    # questions['options'] = (questions['options'])
    # questions['correct_options'] = (questions['correct_options'])
    return render_template('edit_quiz.html', quiz_id=quiz_id, questions=questions)
    
@bp.route('/quiz/delete/<int:quiz_id>', methods=['GET','POST'])
def delete_quiz(quiz_id):
    db = get_db()
    print("Deleting quiz with id:", quiz_id)
    db.execute('DELETE FROM Quizzes WHERE quiz_id = ?', (quiz_id,))
    db.execute('DELETE FROM Questions WHERE quiz_id = ?', (quiz_id,))
    db.execute('DELETE FROM UserResponses WHERE quiz_id = ?', (quiz_id,))
    db.commit()
    return redirect(url_for('interface.dashboard'))

@bp.route('/quiz/start/<int:quiz_id>', methods=['GET','POST'])
def start_quiz(quiz_id):
    db = get_db()
    db.execute('UPDATE Quizzes SET start_time = DATETIME("now","localtime") WHERE quiz_id = ?', (quiz_id,))
    db.commit()
    return redirect(url_for('interface.dashboard'))