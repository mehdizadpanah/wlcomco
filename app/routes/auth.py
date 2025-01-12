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
redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
authorization_base_url = os.getenv('OAUTH_AUTHORIZATION_BASE_URL')
token_url = os.getenv('OAUTH_TOKEN_URL')



@auth_bp.route('/')
def index():
    if current_user.is_authenticated:  # بررسی لاگین بودن کاربر
        # هدایت به dashboard.html
        return redirect(url_for('auth.dashboard'))
    
    return redirect(url_for('auth.login'))  # هدایت به لاگین

@auth_bp.route('/flash-messages')
@login_required
def flash_messages():
    return render_template('includes/_flash_messages.html')
    

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST':  
        if form.validate_on_submit():
            # جستجوی کاربر در پایگاه داده
            user = User.query.filter_by(email=form.email.data).first()
            if user:
                if user.auth_provider == "local":  # بررسی نوع کاربر
                    if user.check_password(form.password.data):  # بررسی رمز عبور
                        login_user(user)
                        return redirect(url_for('auth.dashboard'))
                    flash ('Invalid username or password','danger')
                    return render_template('auth/login.html', form=form)
                flash ("please login using Google",'warning')
                return render_template('auth/login.html', form=form)
            flash ('Invalid username or password','danger')
            return render_template('auth/login.html', form=form)
        
    if form.errors:
        handle_form_errors(form)

    return render_template('auth/login.html',form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    form=SignupForm()
    if request.method == 'POST':
        if form.validate_on_submit():
            # ایجاد کاربر جدید
            new_user = User(auth_provider="local")  # مقداردهی auth_provider به "local"
            if save_user_fields(new_user,form,['name','email','password'],is_new=True):
                # ورود کاربر پس از ثبت‌نام
                login_user(new_user)
                flash ('Welcome! We are glad to have you here.','success')
            return redirect(url_for('auth.dashboard'))
        
        if form.errors:
            handle_form_errors(form)

        return render_template('auth/signup.html',form=form)
        
    # برای لود اولیه فرم، پیام خطا ارسال نمی‌شود
    return render_template('auth/signup.html', form=form, error=None)


@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = ProfileForm()
    
    if request.method == 'POST':
        if form.validate_on_submit():
            # ذخیره اطلاعات فرم در کاربر فعلی
            if save_user_fields(current_user, form, ['name', 'email']):
                flash("Profile updated successfully!", "success")
                return redirect(url_for('auth.dashboard'))  # هدایت به داشبورد در صورت موفقیت
        
        return render_template('auth/profile.html', form=form)

    # مقداردهی اولیه به فرم
    form.name.data = current_user.name
    form.email.data = current_user.email

    # نمایش اولیه صفحه
    return render_template('auth/profile.html', form=form)


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm(email=current_user.email)
    if request.method == 'POST':
        if form.validate_on_submit():
            # بروزرسانی پروفایل کاربر
            if save_user_fields(current_user,form,['password']):
                flash ('Password changed successfully.','success')
                return redirect(url_for('auth.dashboard'))
    
    if request.method == 'GET':
        if current_user.auth_provider == "google":
            flash ('You cannot change your password when you are logged in with your Google account.','info')
            return redirect(url_for('auth.dashboard'))

    if form.errors:
        handle_form_errors(form)

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
        
    return render_template('dashboard.html')
    


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


def save_user_fields(user, form, fields, is_new=False):
    """
    ذخیره یا به‌روزرسانی فیلدهای مشخص‌شده برای کاربر، با پشتیبانی از رمز عبور.
    
    :param user: شیء مدل کاربر (اگر کاربر جدید باشد، شیء باید از نوع User باشد).
    :param form: شیء فرم که داده‌های جدید را در خود دارد.
    :param fields: لیستی از نام فیلدهایی که باید ذخیره یا به‌روزرسانی شوند.
    :param is_new: اگر True باشد، کاربر جدید است و باید به پایگاه داده اضافه شود.
    :return: True اگر تغییری ایجاد یا ذخیره شد، False اگر هیچ تغییری ایجاد نشد.
    """
    updated = False  # برای بررسی تغییرات
    for field in fields:
        if hasattr(user, field) and hasattr(form, field):
            new_value = getattr(form, field).data

            # اگر فیلد password است، از متد set_password استفاده شود
            if field == "password":
                if is_new or not user.check_password(new_value):  # بررسی تغییر رمز عبور
                    user.set_password(new_value)  # هش کردن رمز عبور
                    updated = True
            elif is_new or getattr(user, field) != new_value:  # بررسی تغییر سایر فیلدها
                setattr(user, field, new_value)
                updated = True

    if updated:
        if is_new:  # اگر کاربر جدید است
            db.session.add(user)
        db.session.commit()  # ذخیره تغییرات
        return True
    return False



def handle_form_errors(form):
    for field, errors in form.errors.items():
        if field not in form._fields:
            for error in errors:
                flash(f"{field}: {error}", "danger")
