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
        elif get_db().execute(
            'SELECT quiz_id FROM Quizzes WHERE quiz_id = ?', (quiz_id,)
        ).fetchone() is not None:
            error = f"Quiz {quiz_id} is already registered."
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

    quiz_data = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()
    # print(request.form)
    if request.method == 'POST':
        questions = request.form.getlist('question')
        ques_types = request.form.getlist('ques_type')
        text_answers = request.form.getlist('answer')
        for i in range(len(questions)):
            question = questions[i]
            ques_type = ques_types[i]
            text_answer = text_answers[i]
            hour = request.form.get('hours-' + str(i+1))
            minute = request.form.get('minutes-' + str(i+1))
            second = request.form.get('seconds-' + str(i+1))
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
            options = request.form.getlist('option-' + str(i+1))
            correct_options = request.form.getlist('correct-' + str(i+1))

            db.execute(
                'INSERT INTO Questions (quiz_id, question_id, question_text, question_type, duration)'
                ' VALUES (?, ?, ?, ?, ?)',
                (quiz_id, i+1, question, ques_type, duration)
            )
            if ques_type == 'MCQ':
                for j in range(len(options)):
                    if str(j+1) in correct_options:
                        db.execute(
                            'INSERT INTO Options (quiz_id, question_id, option_id, option_text, correct)'
                            'VALUES (?, ?, ?, ?, ?)',
                            (quiz_id, i+1, j+1, options[j], 1)
                        )
                    else:
                        db.execute(
                            'INSERT INTO Options (quiz_id, question_id, option_id, option_text, correct)'
                            'VALUES (?, ?, ?, ?, ?)',
                            (quiz_id, i+1, j+1, options[j], 0)
                        )
            elif ques_type == 'Text':
                db.execute(
                    'INSERT INTO Options (quiz_id, question_id, option_id, option_text, correct)'
                    'VALUES (?, ?, ?, ?, ?)',
                    (quiz_id, i+1, 1, text_answer, 1)
                )
        db.commit()
        
        return redirect(url_for('quiz.start_time'))
    
    return render_template('add_ques.html', quiz_id=quiz_id, quiz_data=quiz_data)




@bp.route('/user_response', methods=['GET','POST'])
@login_required
def user_response():
    db = get_db()
    quiz = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)).fetchone()
    question = db.execute('SELECT * FROM Questions WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], session['current_question'])).fetchone()
    if request.method == 'POST':
        print(request.form)
        responses = request.form.getlist('response-' + str(session['current_question']))
        responses = ','.join(responses)
        db.execute(
            'INSERT INTO UserResponses (user_id, quiz_id, question_id, selected_options)'
            ' VALUES (?, ?, ?, ?)',
            (g.user['id'], quiz['quiz_id'], session['current_question'], responses)
        )
        db.commit()
        if 'next' in request.form:
            session['current_question'] = int(session['current_question']) + 1
            if question['duration'] != None:
                db.execute('UPDATE Questions SET lock = 1 WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], int(session['current_question']) - 1))
                db.commit()        
            return redirect(url_for('interface.quiz_interface'))
        if 'submit' in request.form:
            if question['duration'] != None:
                db.execute('UPDATE Questions SET lock = 1 WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], int(session['current_question'])))
                db.commit()
            return redirect(url_for('interface.thankyou'))

    return redirect(url_for('interface.quiz_interface'))





@bp.route('/quiz/start_time', methods=('GET', 'POST'))
@admin_login_required
def start_time():
    quiz_id = session['quiz_id']
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
    db.execute('DELETE FROM Options WHERE quiz_id = ?', (quiz_id,))
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
        if lock_unlock == 0:
            db.execute('UPDATE Questions SET unlock_time = ? WHERE quiz_id = ? AND question_id = ?', (db.execute('SELECT DATETIME("now","localtime")').fetchone()[0], quiz_id, question_id))
            db.commit()
        return redirect(url_for('quiz.lock_unlock_ques', quiz_id=quiz_id))
    return render_template('lock_unlock_ques.html', questions=questions, quiz_id=quiz_id)  





@bp.route('/quiz/forced_submit_quiz/<int:quiz_id>', methods=['GET','POST'])
@login_required
def forced_submit_quiz(quiz_id):
    db = get_db()
    db.execute('INSERT INTO UserResponses (user_id, quiz_id, question_id, selected_options) SELECT user_id, quiz_id, question_id, selected_options FROM UserResponses WHERE quiz_id = ?', (quiz_id,))
    return redirect(url_for('interface.dashboard'))