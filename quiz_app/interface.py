from flask import (
    Blueprint, flash, g, redirect, render_template, request, session, url_for, jsonify
)
from quiz_app.db import get_db
from quiz_app.auth import login_required, admin_login_required
import json
from math import radians, cos, sin, asin, sqrt

bp = Blueprint('interface', __name__, url_prefix='/')

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the Earth (specified in decimal degrees).
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371  # Radius of Earth in kilometers. Use 3956 for miles. Determines return value units.
    return c * r

@bp.route('/admin_dashboard', methods=('GET', 'POST'))
@admin_login_required
def admin_dashboard():
    db = get_db()
    if request.method == 'POST':
        # Store admin location
        latitude = request.form.get('latitude')
        longitude = request.form.get('longitude')
        db.execute(
            'UPDATE Admins SET latitude = ?, longitude = ? WHERE admin_id = ?', 
            (latitude, longitude, g.admin['admin_id'])
        )
        db.commit()
        flash("Location updated successfully")
        
    Quizzes = db.execute(
        'SELECT * FROM Quizzes WHERE admin_id = ?', (g.admin['admin_id'],)
    ).fetchall()
    return render_template('admin_dashboard.html', Quizzes=Quizzes)

@bp.route('/update_location/<int:quiz_id>', methods=['POST'])
@login_required
def update_location(quiz_id):
    data = request.get_json()
    latitude = data.get('latitude')
    longitude = data.get('longitude')
    
    db = get_db()
    db.execute(
        'UPDATE Users SET latitude = ?, longitude = ? WHERE id = ?', 
        (latitude, longitude, g.user['id'])
    )
    db.commit()
    
    # Fetch admin location for distance calculation
    admin_location = db.execute(
        'SELECT latitude, longitude FROM Admins WHERE admin_id = (SELECT admin_id FROM Quizzes WHERE quiz_id = ?)', 
        (quiz_id,)
    ).fetchone()
    
    if admin_location:
        admin_lat, admin_lon = admin_location
        distance = haversine(float(longitude), float(latitude), float(admin_lon), float(admin_lat))
        
        # Check if distance is within the allowed range (e.g., 50 km)
        if distance > 50:
            return jsonify({"status": "failure", "message": "You are too far from the admin to participate in this quiz."})
    
    return jsonify({"status": "success", "message": "Location updated successfully"})

@bp.route('/dashboard', methods=('GET', 'POST'))
@login_required
def dashboard():
    error2 = None
    if request.method == 'POST':
        session['current_question'] = 1
        session['quiz_id'] = request.form['quiz_code']
        # Checking if user is blacklisted for that quiz
        if get_db().execute(
            'SELECT * FROM Unfairness WHERE user_id = ? AND quiz_id = ?', (g.user['id'], session['quiz_id'],)).fetchone():
            error2 = "You are blacklisted for this quiz"
        # Checking if user has already attempted the quiz
        elif get_db().execute(
        'SELECT * FROM UserResponses WHERE user_id = ? AND quiz_id = ?', (g.user['id'], session['quiz_id'],)).fetchone():
            error2 = "You have already attempted this quiz"
        # Checking if quiz_id is present in the database
        elif get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)).fetchone() is None:
            error2 = "Quiz not found"
        # Checking if the quiz is started or not
        elif get_db().execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ? AND start_time != ""', (session['quiz_id'],)).fetchone() is None or str(get_db().execute('SELECT * FROM Quizzes WHERE quiz_id = ? ', (session['quiz_id'],)).fetchone()['start_time']) > get_db().execute('SELECT DATETIME("now","localtime")').fetchone()[0]:
            error2 = "Quiz has not started yet"
        else:
            error2 = None
            flash("Quiz Started")
            return redirect(url_for('approve.check_appr_num', quiz_id=session['quiz_id']))
    if error2 is not None:
        flash(error2)
    return render_template('dashboard.html')

@bp.route('/information')
@login_required
def information():
    return render_template('information.html')

@bp.route('/quiz_interface', methods=['GET', 'POST'])
@login_required
def quiz_interface():        
    db = get_db()
    quiz = db.execute(
        'SELECT * FROM Quizzes WHERE quiz_id = ?', (session['quiz_id'],)
    ).fetchone()
    
    # Finding the total number of questions
    ques_count = db.execute(
        'SELECT COUNT(*) FROM Questions WHERE quiz_id = ?', (quiz['quiz_id'],)
    ).fetchone()[0]
    
    # Getting the current questions from the database
    question = db.execute(
        'SELECT * FROM Questions WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], session['current_question'],)
    ).fetchone()
    
    # If unlock_time is None, then it means question is still not unlocked by the admin
    if question['unlock_time'] is None or question['lock'] == 1:
        return redirect(url_for('interface.ques_locked'))
    
    options = db.execute('SELECT * FROM Options WHERE quiz_id = ? AND question_id = ?', (quiz['quiz_id'], question['question_id'])).fetchall()
    
    return render_template('quiz_interface.html', quiz=quiz, ques=question, ques_count=ques_count, options=options, curr_ques= session['current_question'])

@bp.route('/ques_locked')
@login_required
def ques_locked():
    return render_template('ques_locked.html')

@bp.route('/thankyou')
@login_required
def thankyou():
    return render_template('thankyou.html')
