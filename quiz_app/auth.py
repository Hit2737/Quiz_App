from flask import Flask, request, url_for, redirect, render_template, Blueprint
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt
from quiz_app.db import get_db

bp = Blueprint('auth', __name__, url_prefix='/auth')
db = get_db()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(30), unique=True, nullable=False)
    email = db.Column(db.String(60), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class RegisterForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired(), Length(max=30)], render_kw={"placeholder": "Username"})
    email = StringField('Email', validators=[InputRequired(), Length(max=40)], render_kw={"placeholder": "Email"}, description="Email must end with @iitgn.ac.in")
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Register')
    
    def validate_user_email(self, email):
        existing_user_email = User.query.filter_by(email=email.data).first()
        
        if existing_user_email:
            return "Email already exists"
        else:
            return True


class LoginForm(FlaskForm):
    email = StringField('Email', validators=[InputRequired(), Length(max=40)], render_kw={"placeholder": "Email"})
    password = PasswordField('Password', validators=[InputRequired(), Length(min=8, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField('Login')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        # print(user.email)
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            return redirect(url_for('dashboard'))
    
    return render_template('login.html', form=form)

@bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html')

@bp.route('/register',methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    
    if form.validate_on_submit():
        hasher_password = bcrypt.generate_password_hash(form.password.data)
        new_user = User(username=form.username.data, email=form.email.data, password=hasher_password)
        if new_user.email.endswith("iitgn.ac.in"):
            db.session.add(new_user)
            db.session.commit()
            return redirect(url_for('login'))
        else:
            return "Only IITGN email allowed"
        
    return render_template('register.html', form=form)

@bp.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))
