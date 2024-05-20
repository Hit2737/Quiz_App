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
                (quiz_id, quiz_name, g.user['id'])
            )
            db.commit()
            return redirect(url_for('quiz.index'))  # changes karwana chhe url bhaturo jem banave e hisabe

    return render_template('quiz/create_quiz.html')
