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
            correct_options_json = json.dumps(correct_indices) 
            
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
    currenttime = get_db().execute('SELECT CURRENT_TIMESTAMP').fetchone()[0]
    date,time = currenttime.split(' ')
    y,m,d = date.split('-')
    h,min,sec = time.split(':')
    currenttime = y+'-'+m+'-'+d+'T'+h+':'+min
    if request.method == 'POST':
        if 'manual' in request.form:
            return redirect(url_for('interface.dashboard'))
        start_datetime = request.form['start_datetime']+':00.000'
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
    