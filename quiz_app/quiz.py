from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
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
        error = None

        if not question:
            error = 'Question is required.'
        elif not options:
            error = 'Options are required.'

        if error is not None:
            flash(error)
        else:
            options_json = json.dumps(options)  # Convert the options list to a JSON string
            db.execute(
                'INSERT INTO Questions (quiz_id, question_text, options)'
                ' VALUES (?, ?, ?)',
                (quiz_id, question, options_json)
            )
            db.commit()

            if 'add_next' in request.form:
                return redirect(url_for('quiz.add_questions', quiz_id=quiz_id))
            else:
                return render_template('dashboard.html')

    return render_template('addQues.html', quiz_id=quiz_id)
