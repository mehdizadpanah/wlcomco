from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
from .extensions import db
from .extensions import login_manager  # ایمپورت login_manager
from .models import User
from .logging_config import get_logger


# تعریف logger
logger = get_logger(__name__)

# تعریف Blueprint
routes = Blueprint('routes', __name__)

# تنظیمات OAuth برای گوگل
client_id = '640215854838-3nc3pdvsdg5c894jcofljaonj2fomm5g.apps.googleusercontent.com'
client_secret = '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'
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
redirect_uri = 'https://wlcomco.comco.ir/login/google/callback'


@routes.route('/')
def index():
    if current_user.is_authenticated:  # بررسی لاگین بودن کاربر
        return render_template('dashboard.html', name=current_user.name)
  # هدایت به داشبورد
    return redirect(url_for('routes.login'))  # هدایت به لاگین


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@routes.route('/login', methods=['GET', 'POST'])
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
                    return redirect(url_for('routes.dashboard'))
                return render_template('login.html', error="Invalid password")
            return render_template('login.html', error="Please login using Google")
        return render_template('login.html', error="User not found")

    return render_template('login.html')


@routes.route('/signup', methods=['GET', 'POST'])
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
            logger.info('Email already registered')
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
        return redirect(url_for('routes.dashboard'))

    # برای لود اولیه فرم، پیام خطا ارسال نمی‌شود
    return render_template('signup.html', error=None)



@routes.route('/login/google')
def login_google():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['email', 'profile'])
    authorization_url, state = google.authorization_url(
        authorization_base_url,
        access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(authorization_url)


@routes.route('/login/google/callback')
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
    return redirect(url_for('routes.dashboard'))


@routes.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)


@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))
