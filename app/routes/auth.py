import os
from ..models import User,db,Notification
from flask import Blueprint, render_template, redirect, url_for, session, request,current_app ,flash
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
from ..extensions import login_manager,EmailSender  # ایمپورت login_manager
from ..logging_config import get_logger
from app.forms.auth_forms import LoginForm,SignupForm,ProfileForm,ChangePasswordForm,ResendConfirmationForm
from app.forms.auth_forms import SetNewPasswordForm,ResetPasswordForm
from string import Template

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
                    if user.is_email_verified:
                        if user.check_password(form.password.data):  # بررسی رمز عبور
                            login_user(user,remember=form.remember_me.data)
                            flash ('Welcome! We are glad to have you here.','success')
                            return redirect(url_for('auth.dashboard'))
                        flash ('Invalid username or password','danger')
                        return render_template('auth/login.html', form=form)
                    flash('Your email is not verified. <a href="/resend_confirmation">Resend confirmation email</a>', 'warning')
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
            # email_verification_template = Notification.query.filter_by(name="Email Verification").first()
            

            if User.query.filter_by(email=form.email).first():
                 flash ('Email already exist','danger')
                 return redirect(url_for('auth.signup'))
            
            # ایجاد کاربر جدید
            new_user = User(auth_provider="local")  # مقداردهی auth_provider به "local"
            new_user.email = form.email.data
            new_user.set_email_verification_token() #ساخت توکن

            if save_user_fields(new_user,form,['name','email','password'],is_new=True):

                if send_confirmation_email(new_user):
                    flash('Signup successful! Please check your email to verify your account.', 'success')

                return redirect(url_for('auth.login'))
        if form.errors:
            handle_form_errors(form)

        return render_template('auth/signup.html',form=form)
        
    # برای لود اولیه فرم، پیام خطا ارسال نمی‌شود
    return render_template('auth/signup.html', form=form, error=None)


@auth_bp.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    user = User.query.filter_by(email_verification_token=token).first()
    if user and user.verify_email_token(token):
        user.is_email_verified = True
        user.email_verification_token = None
        db.session.commit()
        flash('Email verified successfully!', 'success')
        login_user(user)
        return redirect(url_for('auth.dashboard'))
    
    flash('Invalid or expired token.', 'danger')
    return redirect(url_for('auth.signup'))


@auth_bp.route('/resend_confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    form = ResendConfirmationForm()
    """ریسند کردن لینک تأیید ایمیل برای کاربرانی که ایمیل‌شان تأیید نشده است."""
    # در روش GET صرفاً فرم یا صفحه‌ای برای وارد کردن ایمیل نمایش می‌دهید.
    if request.method == 'GET':
        return render_template('auth/resend_confirmation.html',form = form)  # صفحه‌ای ساده با یک فیلد ایمیل

    if form.validate_on_submit:
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            if user.is_email_verified:
                flash("Your email is already verified!", 'info')
                return redirect(url_for('auth.login'))
            user.set_email_verification_token()
            db.session.commit()
            send_confirmation_email (user)
            flash('Signup successful! Please check your email to verify your account.', 'success')
            return redirect(url_for('auth.login'))

        flash("No account found for this email.", 'danger')
    return render_template('auth/resend_confirmation.html',form = form)
    

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


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    # اگر کاربر وارد سیستم شده، می‌توان او را مستقیماً به داشبورد هدایت کرد
    if current_user.is_authenticated:
        return redirect(url_for('auth.dashboard'))

    form = ResetPasswordForm()

    if request.method == 'POST' and form.validate_on_submit():
        email = form.email.data
        user = User.query.filter_by(email=email).first()

        if not user:
            flash("No user found with this email address.", "danger")
            return redirect(url_for('auth.reset_password'))

        # ایجاد یا به‌روزرسانی توکن بازیابی رمز
        user.set_password_reset_token()  # تابعی مشابه set_email_verification_token
        db.session.commit()

        # ارسال ایمیل بازیابی
        send_reset_password_email(user)
        flash("A reset link has been sent to your email.", "success")
        return redirect(url_for('auth.login'))

    return render_template('auth/reset_password.html', form=form)


@auth_bp.route('/set_new_password/<token>', methods=['GET', 'POST'])
def set_new_password(token):
    form = SetNewPasswordForm()

    # اگر روش درخواست GET است، فرم را نمایش بده
    if request.method == 'GET':
        return render_template('auth/set_new_password.html', form=form, token=token)

    # روش درخواست POST و فرم معتبر باشد
    if form.validate_on_submit():
        user = User.query.filter_by(password_reset_token=token).first()

        if not user:
            flash("Invalid reset link or user not found.", "danger")
            return redirect(url_for('auth.reset_password'))

        # بررسی اعتبار توکن (تاریخ انقضا)
        if not user.verify_password_reset_token(token):
            flash("Reset link expired or invalid.", "danger")
            return redirect(url_for('auth.reset_password'))

        # تنظیم رمز جدید
        user.set_password(form.password.data)
        user.password_reset_token = None
        db.session.commit()

        flash("Your password has been updated. You can now login.", "success")
        return redirect(url_for('auth.login'))

    # اگر خطای ولیدیشن وجود داشت
    return render_template('auth/set_new_password.html', form=form, token=token)


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

def send_confirmation_email(user):

    if user.email and user.email_verification_token:
        email_verification_template = Notification.query.filter_by(name="Email Verification").first()
        confirm_url= url_for('auth.confirm_email', token=user.email_verification_token, _external=True)

        email_body_data = {
            "name":user.name,
            "Confirm_url": confirm_url
        }
        email_body = Template(email_verification_template.body).substitute(email_body_data)
        emailSender = EmailSender()
        emailSender.send_email(subject=email_verification_template.subject, recipients=[user.email],body="", html=email_body)
        return True
    return False

def send_reset_password_email(user):
    if user.email and user.password_reset_token:
        email_password_reset_template = Notification.query.filter_by(name="Reset Password").first()
        confirm_url= url_for('auth.set_new_password', token=user.password_reset_token, _external=True)

        email_body_data = {
            "name":user.name,
            "Reset_url": confirm_url
        }
        email_body = Template(email_password_reset_template.body).substitute(email_body_data)
        emailSender = EmailSender()
        emailSender.send_email(subject=email_password_reset_template.subject, recipients=[user.email],body="", html=email_body)
        return True
    return False
