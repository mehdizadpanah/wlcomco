import os
from ..models import User,db
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
from ..extensions import login_manager  # ایمپورت login_manager
from ..logging_config import get_logger

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
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        # جستجوی کاربر در پایگاه داده
        user = User.query.filter_by(email=email).first()

        if user:
            if user.auth_provider == "local":  # بررسی نوع کاربر
                if user.check_password(password):  # بررسی رمز عبور
                    login_user(user)
                    return redirect(url_for('auth.dashboard'))
                return render_template('login.html', error="Invalid password")
            return render_template('login.html', error="Please login using Google")
        return render_template('login.html', error="User not found")

    return render_template('login.html')


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        # بررسی تطابق رمز عبور
        if password != confirm_password:
            return render_template('signup.html', error="Passwords do not match.")

        # بررسی طول رمز عبور
        if len(password) < 4:
            return render_template('signup.html', error="Password must be at least 4 characters long.")

        # بررسی اینکه آیا ایمیل قبلاً ثبت شده است
        user = User.query.filter_by(email=email).first()
        if user:
            return jsonify({"error": "Email already registered."}), 400

        # ایجاد کاربر جدید
        new_user = User(
            email=email,
            name=name,
            auth_provider="local"  # مقداردهی auth_provider به "local"
        )
        new_user.set_password(password)  # هش کردن رمز عبور
        db.session.add(new_user)
        db.session.commit()

        # ورود کاربر پس از ثبت‌نام
        login_user(new_user)
        return redirect(url_for('auth.dashboard'))

    # برای لود اولیه فرم، پیام خطا ارسال نمی‌شود
    return render_template('signup.html', error=None)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        # بروزرسانی پروفایل کاربر
        name = request.form.get('name')

        # به‌روزرسانی نام کاربر
        current_user.name = name
        db.session.commit()

        return redirect(url_for('auth.dashboard'))
    
    # اطلاعات کاربر فعلی را به قالب ارسال می‌کنیم
    return render_template('profile.html', user=current_user)


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    if request.method == 'POST':
        # بروزرسانی پروفایل کاربر
        password = request.form.get('password')
        current_user.set_password(password)

        db.session.commit()

        return redirect(url_for('auth.dashboard'))
    
    # اطلاعات کاربر فعلی را به قالب ارسال می‌کنیم
    return render_template('change_password.html', name=current_user.name)


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
