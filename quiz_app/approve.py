from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort
from quiz_app.auth import login_required, admin_login_required, approval_required
from quiz_app.db import get_db
from datetime import datetime
import random

bp = Blueprint('approve', __name__, url_prefix='/')

nums = list([])

@bp.route('/appr_num/<int:quiz_id>', methods=('GET', 'POST'))
@admin_login_required
def appr_num(quiz_id,nums=nums):
    session['quiz_id'] = quiz_id
    db = get_db()
    if request.method == 'POST':
        appr_num = request.form['appr_num']
        db.execute('UPDATE Quizzes SET appr_num = ? WHERE quiz_id = ?', (appr_num, quiz_id))
        db.commit()
        flash('Approval Number is set Successfully.')
        return redirect(url_for('quiz.start_quiz',quiz_id=quiz_id))
    nums[0:3] = random.sample(range(1, 100), 3)
    return render_template('admin_appr_no.html',quiz_id=quiz_id,nums=nums)


@bp.route('/check_appr_num/<int:quiz_id>', methods=('GET', 'POST'))
@login_required
def check_appr_num(quiz_id,nums=nums):
    db = get_db()
    user = db.execute('SELECT * FROM Approvals WHERE user_id = ? and quiz_id = ?',(session['user_id'],quiz_id)).fetchone()
    if user != None and user['approval_status'] == 0:
        flash("You failed to get approved. Now you can't access this quiz.")
        return redirect(url_for('interface.dashboard'))
    elif user != None and user['approval_status'] == 1:
        flash("You are already approved.")
        return redirect(url_for('interface.quiz_interface', success=""))
    if request.method == 'POST':
        appr_num = db.execute('SELECT * FROM Quizzes WHERE quiz_id = ?', (quiz_id,)).fetchone()['appr_num']
        if appr_num == int(request.form['selected_num']):
            flash('You are approved.')
            db.execute('INSERT INTO Approvals (user_id, quiz_id, approval_status, time_stamp) VALUES (?,?,?,?)',(session['user_id'],quiz_id,1,db.execute('SELECT DATETIME("now", "localtime")').fetchone()[0]))
            db.commit()
            return redirect(url_for('interface.quiz_interface', success=""))
        else:
            flash('You are not approved.')
            db.execute('INSERT INTO Approvals (user_id, quiz_id, approval_status, time_stamp) VALUES (?,?,?,?)',(session['user_id'],quiz_id,0,db.execute('SELECT DATETIME("now", "localtime")').fetchone()[0]))
            db.commit()
            return redirect(url_for('interface.dashboard'))
    return render_template('check_appr_num.html',nums=nums,quiz_id=quiz_id)

@bp.route('/is_fair/<int:quiz_id>', methods=['POST'])
@login_required
def is_fair(quiz_id):
    db = get_db()
    data = request.get_json()
    user = db.execute('SELECT * FROM Unfairness WHERE user_id = ? AND quiz_id = ?',(session['user_id'],quiz_id)).fetchone()
    if user != None and user['unfairness_status'] == 1:
        flash("You are not allowed to access this quiz.")
        return redirect(url_for('interface.dashboard'))
    if data['hidden'] and user == None:
        print("Unfairness detected")
        db.execute('INSERT INTO Unfairness (user_id, quiz_id, unfairness_status, time_stamp) VALUES (?,?,?,?)',(session['user_id'],quiz_id,1,db.execute('SELECT DATETIME("now", "localtime")').fetchone()[0]))
        db.commit()
    return redirect(url_for('interface.dashboard'))