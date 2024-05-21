import functools

from flask import(
    Blueprint, flash, g, redirect, render_template, request, session, url_for
)
from werkzeug.security import check_password_hash, generate_password_hash

from quiz_app.db import get_db

import json
bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get('user_id')

    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM user WHERE id = ?', (user_id,)
        ).fetchone()
    
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view

# INSERT INTO Questions (quiz_id, question_text, options) VALUES 
# (1, 'What is the capital of France?', '[{"option_text": "Paris", "is_correct": true}, {"option_text": "London", "is_correct": false}, {"option_text": "Berlin", "is_correct": false}, {"option_text": "Delhi", "is_correct": false}]');

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
    if request.method == 'POST':
        session['current_question'] = session['current_question'] + 1
        if(session['current_question'] > ques_count[0]):
            return redirect(url_for('auth.thankyou'))
        return redirect(url_for('auth.student_interface'))
    try:
        options = current_question['options']
        options = json.loads(options)
    except:
        return redirect(url_for('auth.dashboard'))
        
    return render_template('student_interface.html' ,quiz=quiz, ques=current_question, ques_count=ques_count[0], options=options)

@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        error = None

        if not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO user (username, password) VALUES (?, ?)",
                    (username, generate_password_hash(password)),
                )
                db.commit()
            except db.IntegrityError:
                error = f"User {username} is already registered."
            else:
                return redirect(url_for("auth.login"))

        flash(error)

    return render_template('auth/register.html')


@bp.route('/thankyou')
@login_required
def thankyou():
    return render_template('thankyou.html')


@bp.route('/login', methods=('GET', 'POST'))
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        quiz_code = request.form['quiz_code']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        quiz = db.execute(
            'SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_code,)
        ).fetchone()
        if quiz is None:
            error = 'Invalid Quiz Code.'
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['quiz_id'] = quiz['quiz_id']
            session['current_question'] = 1
            print(session)
            return redirect(url_for('auth.student_interface'));

        flash(error)

    return render_template('auth/login.html')

@bp.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    Quizzes = get_db().execute(
        'SELECT * FROM Quizzes'
    ).fetchall()
    if(request.method == 'POST'):
        session['current_question'] = 1
        session['quiz_id'] = request.form['quiz_code']
        print(session)
        return redirect(url_for('auth.student_interface'))
    return render_template('dashboard.html', Quizzes=Quizzes)