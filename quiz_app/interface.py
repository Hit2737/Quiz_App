from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from quiz_app.db import get_db
from quiz_app.auth import login_required, admin_login_required
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
    Quizzes = get_db().execute(
        'SELECT * FROM Quizzes'
    ).fetchall()
    error2 = None
    if(request.method == 'POST'):
        session['current_question'] = 1
        session['quiz_id'] = request.form['quiz_code']
        if get_db().execute(
        'SELECT * FROM UserResponses WHERE user_id = ? AND quiz_id = ?', (g.user['id'], session['quiz_id'],)).fetchone():
            error2 = "You have already attempted this quiz"
        elif get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)).fetchone() is None:
            error2 = "Quiz not found"
        elif get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ? AND start_time != ""', (session['quiz_id'],)).fetchone() is None or str(get_db().execute(
            'SELECT * FROM Quizzes WHERE quiz_id = ? ', (session['quiz_id'],)).fetchone()['start_time']) > get_db().execute('SELECT DATETIME("now","localtime")').fetchone()[0]:
            error2 = "Quiz has not started yet"
        else:
            error2 = None
            flash("Quiz Started")
            return redirect(url_for('interface.information'))
    if error2 is not None:
        flash(error2)
    return render_template('dashboard.html', Quizzes=Quizzes)

@bp.route('/information', methods=('GET', 'POST'))
@login_required
def information():
    return render_template('information.html')

@bp.route('/student_interface', methods=('GET', 'POST'), endpoint='student_interface')
@login_required
def student_interface():
    quiz = get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)
    ).fetchone()
    ques_count = get_db().execute(
        'SELECT COUNT(*) FROM Questions WHERE quiz_id = ?', (quiz['quiz_id'],)
    ).fetchone()
    current_question = get_db().execute(
        'SELECT * FROM Questions WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], session['current_question'],)
    ).fetchone()
    if(int(session['current_question']) > ques_count[0]):
        return redirect(url_for('interface.thankyou'))
    if current_question['duration'] is None:
        if current_question['lock'] == 1:
            return redirect(url_for('interface.ques_locked'))
        else:
            options = current_question['options']
            options = json.loads(options)
            return render_template('student_interface.html' ,quiz=quiz, ques=current_question, ques_count=ques_count[0], options=options, duration=-1)
    
    options = current_question['options']
    options = json.loads(options)
    return render_template('student_interface.html' ,quiz=quiz, ques=current_question, ques_count=ques_count[0], options=options, duration=1)

@bp.route('/ques_locked')
@login_required
def ques_locked():
    return render_template('ques_locked.html')

@bp.route('/thankyou')
@login_required
def thankyou():
    return render_template('thankyou.html')
    
