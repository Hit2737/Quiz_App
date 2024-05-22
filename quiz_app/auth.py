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
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM user WHERE username = ?', (username,)
        ).fetchone()
        if user is None:
            error = 'Incorrect username.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            session['current_question'] = 1
            print(session)
            return redirect(url_for('auth.dashboard'))

        flash(error)

    return render_template('auth/login.html')

@bp.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    Quizzes = get_db().execute(
        'SELECT * FROM Quizzes'
    ).fetchall()
    print("hello\n\n")
    print(Quizzes)
    if(request.method == 'POST'):
        session['current_question'] = 1
        session['quiz_id'] = request.form['quiz_code']
        print(session)
        return redirect(url_for('auth.student_interface'))
    return render_template('dashboard.html', Quizzes=Quizzes)

@bp.route('/submit_response/<quiz_id>/<question_id>', methods=['POST'])
@login_required
def submit_response(quiz_id, question_id):
    db = get_db()
    user_id = g.user['id']
    selected_options = request.form.getlist('selected_option')
    print("Form Data:", request.form)  # Print the entire form data for debugging
    print("Selected Options:", selected_options)  # Print selected options
    if not selected_options:
        flash('You must select at least one option.')
        session['current_question'] = question_id
        session['quiz_id'] = quiz_id
        return redirect(url_for('auth.student_interface'))
    selected_options_indices = [int(option) for option in selected_options] 
    selected_options_json = json.dumps(selected_options_indices)  # Convert the list to a JSON string
    print(selected_options_json)
    db.execute(
        'INSERT INTO UserResponses (user_id, quiz_id, question_id, selected_options)'
        ' VALUES (?, ?, ?, ?)',
        (user_id, quiz_id, question_id, selected_options_json)
    )
    db.commit()

    next_question_id = int(question_id) + 1
    # Check if there are more questions
    next_question = db.execute(
        'SELECT * FROM Questions WHERE quiz_id = ? AND question_id = ?',
        (quiz_id, next_question_id)
    ).fetchone()

    if next_question is None:
        return redirect(url_for('auth.thankyou'))
    else:
        session['current_question'] = next_question_id
        session['quiz_id'] = quiz_id
        return redirect(url_for('auth.student_interface'))

# @bp.route('/take-quiz/<quiz_id>/<int:question_id>', methods=['GET'])
# @login_required
# def take_quiz(quiz_id, question_id):
#     db = get_db()
#     question = db.execute(
#         'SELECT * FROM Questions WHERE quiz_id = ? AND id = ?',
#         (quiz_id, question_id)
#     ).fetchone()

#     if question is None:
#         abort(404)

#     options = json.loads(question['options'])  # Convert JSON string back to list
#     return render_template('quiz.html', question=question, options=options, quiz_id=quiz_id)