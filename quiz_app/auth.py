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
    admin_id = session.get('admin_id')
    if admin_id is None:
        g.admin = None
    else:
        g.admin = get_db().execute(
            'SELECT * FROM Admins WHERE admin_id = ?', (admin_id,)
        ).fetchone()
    if user_id is None:
        g.user = None
    else:
        g.user = get_db().execute(
            'SELECT * FROM Users WHERE id = ?', (user_id,)
        ).fetchone()
    
@bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login_student'))
        return view(**kwargs)
    return wrapped_view

def admin_login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if g.admin is None:
            return redirect(url_for('auth.login_admin'))
        return view(**kwargs)
    return wrapped_view


def approval_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        user = get_db().execute('SELECT * FROM Approvals WHERE user_id = ? AND quiz_id= ? AND approval_status = 1', (g.user['id'],session['quiz_id'])).fetchone();
        if user != None and user['approval_status'] == 0:
            return redirect(url_for('interface.dashboard'))
        if user == None:
            return redirect(url_for('approve.check_appr_num',quiz_id=session['quiz_id']))
        return view(**kwargs)
    return wrapped_view


@bp.route('/register', methods=('GET', 'POST'))
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email_id = request.form['email_id']
        db = get_db()
        error = None

        if not email_id.endswith('@iitgn.ac.in'):
            error = 'You must login from your IITGN email id.'
        elif not username:
            error = 'Username is required.'
        elif not password:
            error = 'Password is required.'

        if error is None:
            try:
                db.execute(
                    "INSERT INTO Users (username, password, email_id) VALUES (?, ?, ?)",
                    (username, generate_password_hash(password), email_id),
                )
                db.commit()
                return redirect(url_for("auth.login_student"))  
            except db.IntegrityError:
                error = f"Username or Email is already registered."
        flash(error)
    return render_template('auth/register.html')


@bp.route('/login_student', methods=('GET', 'POST'))
def login_student():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Users WHERE email_id = ?', (email,)
        ).fetchone()
        if user is None:
            error = 'Please check you email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['user_id'] = user['id']
            return redirect(url_for('interface.dashboard'))

        flash(error)

    return render_template('auth/login_student.html')

@bp.route('/login_admin', methods=('GET', 'POST'))
def login_admin():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        db = get_db()
        error = None
        user = db.execute(
            'SELECT * FROM Admins WHERE email_id = ?', (email,)
        ).fetchone()
        if user is None:
            error = 'Please check you email.'
        elif not check_password_hash(user['password'], password):
            error = 'Incorrect password.'

        if error is None:
            session.clear()
            session['admin_id'] = user['admin_id']
            return redirect(url_for('interface.admin_dashboard'))

        flash(error)

    return render_template('auth/login_admin.html')

