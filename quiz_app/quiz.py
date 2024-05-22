from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from werkzeug.exceptions import abort
from quiz_app.auth import login_required
from quiz_app.db import get_db

bp = Blueprint('quiz', __name__)

@bp.route('/create', methods=('GET', 'POST'))
@login_required
def create():
    print("hello")
    if request.method == 'POST':
        print("hel")
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
                (quiz_id, quiz_name, g.user['id'])
            )
            db.commit()
            return redirect(url_for('quiz.add_questions',quiz_id=quiz_id))  # changes karwana chhe url bhaturo jem banave e hisabe

    return render_template('create_quiz.html')


@bp.route('/add-questions/<quiz_id>', methods=('GET', 'POST'))
@login_required
def add_questions(quiz_id):
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
            db = get_db()
            db.execute(
                'INSERT INTO Questions (quiz_id, question_text)'
                ' VALUES (?, ?)',
                (quiz_id, question)
            )
            question_id = db.execute('SELECT last_insert_rowid()').fetchone()[0]
            for option in options:
                db.execute(
                    'INSERT INTO Options (question_id, option_text)'
                    ' VALUES (?, ?)',
                    (question_id, option)
                )
            db.commit()

            if 'add_next' in request.form:
                return redirect(url_for('quiz.add_questions', quiz_id=quiz_id))
            else:
                return redirect(url_for('quiz.index'))

    return render_template('addQues.html', quiz_id=quiz_id)
