from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from quiz_app.db import get_db
from quiz_app.auth import login_required, admin_login_required, approval_required
import json
bp = Blueprint('interface', __name__, url_prefix='/')

@bp.route('/admin_dashboard', methods=('GET', 'POST'))
@admin_login_required
def admin_dashboard():
    Quizzes = get_db().execute(
        'SELECT * FROM Quizzes WHERE admin_id = ?', (g.admin['admin_id'],)
    ).fetchall()
    return render_template('admin_dashboard.html', Quizzes=Quizzes)


@bp.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    error2 = None
    session['success'] = ""
    if(request.method == 'POST'):
        session['current_question'] = 1
        session['quiz_id'] = request.form['quiz_code']
        # Checking if user is black listed for that quiz
        if get_db().execute(
            'SELECT * FROM Unfairness WHERE user_id = ? AND quiz_id = ?', (g.user['id'], session['quiz_id'],)).fetchone():
            error2 = "You are blacklisted for this quiz"
        # Checking if user has already attempted the quiz
        elif get_db().execute(
        'SELECT * FROM UserResponses WHERE user_id = ? AND quiz_id = ?', (g.user['id'], session['quiz_id'],)).fetchone():
            error2 = "You have already attempted this quiz"
        # Checking if quiz_id is present in the database
        elif get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)).fetchone() is None:
            error2 = "Quiz not found"
        # Checking if the quiz is started or not
        elif get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ? AND start_time != ""', (session['quiz_id'],)).fetchone() is None or str(get_db().execute('SELECT * FROM Quizzes WHERE quiz_id = ? ', (session['quiz_id'],)).fetchone()['start_time']) > get_db().execute('SELECT DATETIME("now","localtime")').fetchone()[0]:
            error2 = "Quiz has not started yet"
        
        else:
            error2 = None
            flash("Quiz Started")
            return redirect(url_for('interface.information',quiz_id=session['quiz_id']))
    if error2 is not None:
        flash(error2)
    return render_template('dashboard.html')




@bp.route('/information')
@login_required
def information():
    return render_template('information.html')




@bp.route('/quiz_interface', methods=['GET', 'POST'])
@login_required
@approval_required
def quiz_interface(success = ""):      
    db = get_db()
    quiz = db.execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)
    ).fetchone()

    # Finding the total number of questions
    ques_count = db.execute(
        'SELECT COUNT(*) FROM Questions WHERE quiz_id = ?', (quiz['quiz_id'],)
    ).fetchone()[0]

    # Getting the current questions from the database
    question = db.execute(
        'SELECT * FROM Questions WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], session['current_question'],)
    ).fetchone()
    
    # If unlock_time is None, then it means question is still not unlocked by the admin
    if question['unlock_time'] is None or question['lock'] == 1:
        return redirect(url_for('interface.ques_locked', successfull = session['success']))

    options = db.execute('SELECT * FROM Options WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'],question['question_id'])).fetchall()
    
    return  render_template('quiz_interface.html' ,quiz=quiz, ques=question, ques_count=ques_count, options=options,curr_ques= session['current_question'])
    



@bp.route('/ques_locked')
@login_required
def ques_locked(success = ""):
    return render_template('ques_locked.html', successfull = session['success'])




@bp.route('/thankyou')
@login_required
@approval_required
def thankyou(suceess = False):
    return render_template('thankyou.html', quiz_id = session['quiz_id'], successfull = session['success'])
    
    
    

@bp.route('/report', methods=['GET','POST'])
@login_required
def report():
    db = get_db()
    if request.method == 'POST':
        quiz_id = request.form['quiz_code']
        session['quiz_id'] = quiz_id
    else:
        quiz_id = session['quiz_id']
    quiz = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()
    
    if(quiz == None):
        flash("Quiz not found")
        return redirect(url_for('interface.dashboard'))
    
    responses = db.execute('SELECT * FROM UserResponses WHERE quiz_id = ? AND user_id = ?', (quiz_id, g.user['id'])).fetchone()
    if(responses is None):
        flash("No responses found")
        return redirect(url_for('interface.dashboard'))
    responses = db.execute('SELECT * FROM UserResponses WHERE quiz_id = ? AND user_id = ?', (quiz_id, g.user['id'])).fetchall()
    questions = db.execute('SELECT * FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchall()
    options = db.execute('SELECT * FROM Options WHERE quiz_id = ?', (quiz_id,)).fetchall()
    
    selected_options = {}
    
    for resp in responses:
        sel_op = str(resp['selected_options'])
        print(sel_op)
        selected_options[resp['question_id']] = sel_op.split(',')
    
    for (key, value) in selected_options.items():
        try :
            selected_options[key] = [int(i) for i in value]
        except:
            pass
    
    return render_template('report.html', quiz=quiz, responses=responses, questions=questions, options=options, selected_options=selected_options)
    
    