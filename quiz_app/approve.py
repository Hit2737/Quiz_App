from flask import Blueprint, flash, g, redirect, render_template, request, url_for, session
from werkzeug.exceptions import abort
from quiz_app.auth import login_required
from quiz_app.db import get_db
from datetime import datetime

bp = Blueprint('approve', __name__, url_prefix='/')

@bp.route('/approve_users', methods=('GET', 'POST'))
@login_required
def approve_users():
    db = get_db()
    
    # Fetch all users except the current approver
    users = db.execute(
        'SELECT id, username FROM Users WHERE id != ?', (g.user['id'],)
    ).fetchall()
    
    if request.method == 'POST':
        approved_usernames = request.form.getlist('approved_users')
        if approved_usernames:
            quiz_id = session.get('quiz_id', None)
            
            if quiz_id:
                approver_id = g.user['id']
                for username in approved_usernames:
                    approved_user = db.execute(
                        'SELECT id FROM Users WHERE username = ?', (username,)
                    ).fetchone()
                    
                    if approved_user:
                        db.execute(
                            'INSERT INTO ApprovedUsers (approver_id, approved_id, quiz_id, approval_time)'
                            ' VALUES (?, ?, ?, ?)',
                            (approver_id, approved_user['id'], quiz_id, datetime.now())
                        )
                
                db.commit()
                flash('Users approved successfully.')
                return redirect(url_for('interface.quiz_interface'))
            else:
                flash('Quiz ID not found in session.')
        else:
            flash('No users selected for approval.')
    
    return render_template('approval.html', users=users)
