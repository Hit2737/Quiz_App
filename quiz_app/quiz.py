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
        error = None

        if not question:
            error = 'Question is required.'
        elif not options:
            error = 'Options are required.'

        if error is not None:
            flash(error)
        else:
            result= db.execute('SELECT MAX(question_id) FROM Questions WHERE quiz_id = ?', (quiz_id,)).fetchone()
            next_question_id= (result[0] or 0) + 1
            options_json = json.dumps(options)  # Convert the options list to a JSON string
            
            correct_indices = [index for index, value in enumerate(correct_options) if value == 'on']
            correct_options_json = json.dumps(correct_indices) 
            
            db.execute(
                'INSERT INTO Questions (question_id, quiz_id, question_text, options, correct_options)'
                ' VALUES (?, ?, ?, ?, ?)',
                (next_question_id, quiz_id, question, options_json, correct_options_json)
            )
            db.commit()

            if 'add_next' in request.form:
                return redirect(url_for('quiz.add_questions', quiz_id=quiz_id))
            else:
                return redirect(url_for('interface.dashboard'))

    return render_template('addQues.html', quiz_id=quiz_id)

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
        return redirect(url_for('interface.student_interface'))
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
        return redirect(url_for('interface.thankyou'))
    else:
        session['current_question'] = next_question_id
        session['quiz_id'] = quiz_id
        return redirect(url_for('interface.student_interface'))