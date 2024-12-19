import os
from ..models import User,db
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify,flash
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
from ..extensions import login_manager  # ایمپورت login_manager
from ..logging_config import get_logger
from app.forms.auth_forms import LoginForm,SignupForm,ProfileForm,ChangePasswordForm

# تعریف logger
logger = get_logger(__name__)

# تعریف Blueprint
auth_bp = Blueprint('auth', __name__)

# تنظیمات OAuth برای گوگل
client_id = os.getenv('OAUTH_CLIENT_ID')
client_secret = os.getenv('OAUTH_CLIENT_SECRET')
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
redirect_uri = os.getenv('OAUTH_REDIRECT_URI')


@auth_bp.route('/')
def index():
    if current_user.is_authenticated:  # بررسی لاگین بودن کاربر
        return render_template('dashboard.html', name=current_user.name)
  # هدایت به داشبورد
    return redirect(url_for('auth.login'))  # هدایت به لاگین


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':  
        if form.validate_on_submit():
            email = form.email.data
            password = form.password.data

            # جستجوی کاربر در پایگاه داده
            user = User.query.filter_by(email=email).first()

            if user:
                if user.auth_provider == "local":  # بررسی نوع کاربر
                    if user.check_password(password):  # بررسی رمز عبور
                        login_user(user)
                        return redirect(url_for('auth.dashboard'))
                    flash ('Invalid username or password','danger')
                    return render_template('auth/login.html', form=form)
                flash ("please login using Google",'warning')
                return render_template('auth/login.html', form=form)
            flash ('Invalid username or password','danger')
            return render_template('auth/login.html', form=form)
        flash ('Your data entry is not valid','danger')
        return render_template('auth/login.html',form=form)

    return render_template('auth/login.html',form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form=SignupForm()
    if request.method == 'POST':
        email = form.email.data
        name  = form.name.data
        password = form.password.data
        confirm_password = form.confirm_password.data
        
        # بررسی اینکه آیا ایمیل قبلاً ثبت شده است
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"error": "Email already registered."}), 400

        if form.validate_on_submit:
            # ایجاد کاربر جدید
            new_user = User(
            email=email,
            name=name,
            auth_provider="local")  # مقداردهی auth_provider به "local"

            new_user.set_password(password)  # هش کردن رمز عبور
            db.session.add(new_user)
            db.session.commit()

            # ورود کاربر پس از ثبت‌نام
            login_user(new_user)
            flash ('Welcome! We are glad to have you here.','success')
            return redirect(url_for('auth.dashboard'))
        
        flash ('Your data is not validating','error')
        return render_template('auth/signup.html',form=form)
        
    # برای لود اولیه فرم، پیام خطا ارسال نمی‌شود
    return render_template('auth/signup.html', form=form, error=None)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    if request.method == 'POST':
        # به‌روزرسانی نام کاربر
        isChange = False
        if current_user.name != form.name.data:
            isChange = True
        if isChange == True:
            current_user.name = form.name.data
            db.session.commit()
            flash("Profile updated successfully!", "success")
        return redirect(url_for('auth.dashboard'))
    
    if request.method == 'GET':
        # اطلاعات کاربر فعلی را به قالب ارسال می‌کنیم
        form.name.data = current_user.name
        form.email.data = current_user.email
    return render_template('auth/profile.html', form=form)


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if request.method == 'POST':
        # بروزرسانی پروفایل کاربر
        current_user.set_password(form.password.data)

        db.session.commit()
        flash ('Password changed successfully.','success')
        return redirect(url_for('auth.dashboard'))
    
    # اطلاعات کاربر فعلی را به قالب ارسال می‌کنیم
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/login/google')
def login_google():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['email', 'profile'])
    authorization_url, state = google.authorization_url(
        authorization_base_url,
        access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(authorization_url)


@auth_bp.route('/login/google/callback')
def callback():
    google = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    token = google.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(email=user_info['email'], name=user_info['name'], auth_provider="google")
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('auth.dashboard'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))
