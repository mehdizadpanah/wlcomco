import os
from ..models import User,db,Notification
from flask import Blueprint, render_template, redirect, url_for, session, request,current_app ,flash
from flask_login import login_user, logout_user, login_required, current_user
from requests_oauthlib import OAuth2Session
from ..extensions import login_manager,EmailSender ,RedisClient,get_logger,UnitUtils # ایمپورت login_manager
from app.forms.auth_forms import LoginForm,SignupForm,ProfileForm,ChangePasswordForm,ResendConfirmationForm
from app.forms.auth_forms import SetNewPasswordForm,ResetPasswordForm
from string import Template

# تعریف Blueprint
auth_bp = Blueprint('auth', __name__)

logger = get_logger('routes')

# تنظیمات OAuth برای گوگل
client_id = os.getenv('OAUTH_CLIENT_ID')
client_secret = os.getenv('OAUTH_CLIENT_SECRET')
redirect_uri = os.getenv('OAUTH_REDIRECT_URI')
authorization_base_url = os.getenv('OAUTH_AUTHORIZATION_BASE_URL')
token_url = os.getenv('OAUTH_TOKEN_URL')



@auth_bp.route('/')
def index():
    logger.info('Index route called.')
    if current_user.is_authenticated:  # بررسی لاگین بودن کاربر
        # هدایت به dashboard.html
        return redirect(url_for('auth.dashboard'))
    return redirect(url_for('auth.login'))  # هدایت به لاگین


# @auth_bp.route('/flash-messages')
# @login_required
# def flash_messages():
#     return render_template('includes/_flash_messages.html')
    

@login_manager.user_loader
def load_user(user_id):
    try:
        # logger.info(f'Attempting to load user with ID: {user_id}')
        user = User.query.get(UnitUtils.hex_to_bytes(user_id))
        # user = User.query.get(int(user_id))
        # if user:
            # logger.info(f'User {user.name} (ID: {user_id}) loaded successfully.')
        # else:
            # logger.warning(f'User with ID {user_id} not found.')

        return user
    
    except ValueError as ve:
        # مدیریت خطاهای مقدار نامعتبر
        logger.error(f'Invalid user_id provided: {user_id}. Error: {ve}')
        return None
    
    except Exception as e:
        # مدیریت خطاهای عمومی
        logger.critical(f'Unexpected error while loading user with ID: {user_id}. Error: {e}')
        return None


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    متد لاگین کاربران
    """
    logger.info('Login endpoint accessed.')
    form = LoginForm()

    try:
        if request.method == 'POST':  
            logger.info('POST request received for login.')

            if form.validate_on_submit():
                logger.info(f"Form validated successfully for email: {form.email.data}")

                # جستجوی کاربر در پایگاه داده
                user = User.get_by_email(form.email.data)
                if user:
                    logger.info(f"User found with email: {form.email.data}")

                    if user.auth_provider == "local":  # بررسی نوع کاربر
                        logger.info("User authentication provider is local.")

                        if user.is_email_verified:
                            logger.info("User's email is verified.")
                    
                            if user.check_password(form.password.data):  # بررسی رمز عبور
                                logger.info(f"User {user.email} logged in successfully.")
                                login_user(user,remember=form.remember_me.data)
                                flash ('Welcome! We are glad to have you here.','success')
                                return redirect(url_for('auth.dashboard'))

                            logger.warning(f"Invalid password attempt for user: {user.email}")
                            flash ('Invalid username or password','danger')
                            return render_template('auth/login.html', form=form)

                        logger.warning(f"User {user.email} tried to log in with unverified email.")
                        flash('Your email is not verified. <a href="/resend_confirmation">Resend confirmation email</a>', 'warning')
                        return render_template('auth/login.html', form=form)

                    logger.warning(f"User {user.email} attempted to log in with unsupported auth provider: {user.auth_provider}.")
                    flash ("please login using Google",'warning')
                    return render_template('auth/login.html', form=form)

                logger.warning(f"Login attempt failed for non-existent email: {form.email.data}")
                flash ('Invalid username or password','danger')
                return render_template('auth/login.html', form=form)
        
        if form.errors:
            logger.warning(f"Form validation errors: {form.errors}")

    except Exception as e:
        logger.critical(f"Unexpected error in login route: {str(e)}")
        flash('An unexpected error occurred. Please try again later.', 'danger')

    logger.info("Rendering login page.")
    return render_template('auth/login.html',form=form)


@auth_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    متد برای ثبت‌نام کاربران جدید
    """
    logger.info('Signup endpoint accessed.')
    form=SignupForm()
    try:

        if request.method == 'POST':
            logger.info('POST request received for signup.')

            if form.validate_on_submit():
                logger.info(f"Form validated successfully for email: {form.email.data}")
            
                # بررسی وجود ایمیل
                if User.get_by_email(form.email.data):
                    logger.warning(f"Attempt to register with existing email: {form.email.data}")
                    flash ('Email already exist','danger')
                    return redirect(url_for('auth.signup'))
            
                # ایجاد کاربر جدید
                logger.info(f"Creating new user with email: {form.email.data}")
                new_user = User(auth_provider="local")  # مقداردهی auth_provider به "local"
                new_user.email = form.email.data
                new_user.set_token('email-confirm') #ساخت توکن

                if save_user_fields(new_user,form,['name','email','password']):
                    logger.info(f"User {new_user.email} saved successfully.")

                    # ارسال ایمیل تایید
                    if send_confirmation_email(new_user):
                        logger.info(f"Confirmation email sent to send email method")
                        flash('Signup successful! Please check your email to verify your account.', 'success')
                    else:
                        logger.error(f"Failed to send confirmation email to {new_user.email}")

                    return redirect(url_for('auth.login'))
            if form.errors:
                logger.warning(f"Form validation errors: {form.errors}")

        return render_template('auth/signup.html', form=form)

    except Exception as e:
        logger.critical(f"Unexpected error in signup route: {str(e)}")
        flash('An unexpected error occurred during signup. Please try again later.', 'danger')
        return render_template('auth/signup.html', form=form)


@auth_bp.route('/confirm_email/<token>', methods=['GET'])
def confirm_email(token):
    """
    متد برای تایید ایمیل کاربران
    """
    logger.info('Email confirmation endpoint accessed.')
    try:
        # جستجوی کاربر بر اساس توکن
        user = User.get_by_token(token,'email_verification_token')
        if user:
            logger.info(f"User found with email: {user.email}. Verifying token...")
            
            if user.verify_token(token,'email-confirm'):
                logger.info(f"Token verified successfully for user: {user.email}.")

                # بروزرسانی وضعیت ایمیل کاربر
                user.is_email_verified = True
                user.email_verification_token = None
                db.session.commit()
                logger.info(f"Email verified and token cleared for user: {user.email}.")

                flash('Email verified successfully!', 'success')
                login_user(user)
                return redirect(url_for('auth.dashboard'))
        
            else:
                logger.warning(f"Token verification failed for user: {user.email}.")
        else:
            logger.warning("User not found with the provided token.")

        # اگر توکن نامعتبر یا منقضی باشد
        flash('Invalid or expired token.', 'danger')
        logger.warning("Invalid or expired token used.")
        return redirect(url_for('auth.signup'))

    except Exception as e:
        logger.critical(f"Unexpected error during email confirmation: {str(e)}")
        flash('An unexpected error occurred during email confirmation. Please try again later.', 'danger')
        return redirect(url_for('auth.signup'))


@auth_bp.route('/resend_confirmation', methods=['GET', 'POST'])
def resend_confirmation():
    """
    ارسال مجدد لینک تأیید ایمیل برای کاربرانی که ایمیل آن‌ها تأیید نشده است.
    """
    logger.info('Resend confirmation endpoint accessed.')
    form = ResendConfirmationForm()

    try:
        if request.method == 'GET':
            logger.info('GET request received for resend confirmation.')
            return render_template('auth/resend_confirmation.html', form=form)  # نمایش فرم

        if form.validate_on_submit():
            logger.info(f"Form validated successfully for email: {form.email.data}")
            user = User.get_by_email(form.email.data)

            if user:
                logger.info(f"User found with email: {user.email}")
                if user.is_email_verified:
                    logger.info(f"User {user.email} already verified.")
                    flash("Your email is already verified!", 'info')
                    return redirect(url_for('auth.login'))

                # ایجاد توکن جدید برای تأیید ایمیل
                user.set_token('email-confirm')
                db.session.commit()
                logger.info(f"New email verification token generated for user: {user.email}")

                # ارسال ایمیل تأیید
                if send_confirmation_email(user):
                    logger.info(f"Confirmation email resent to send email method")
                    flash('Signup successful! Please check your email to verify your account.', 'success')
                else:
                    logger.error(f"Failed to send confirmation email to {user.email}")
                    flash('Failed to resend confirmation email. Please try again later.', 'danger')

                return redirect(url_for('auth.login'))

            # کاربر با ایمیل وارد شده پیدا نشد
            logger.warning(f"No account found for email: {form.email.data}")
            flash("No account found for this email.", 'danger')

        if form.errors:
            logger.warning(f"Form validation errors: {form.errors}")

    except Exception as e:
        logger.critical(f"Unexpected error in resend confirmation route: {str(e)}")
        flash('An unexpected error occurred. Please try again later.', 'danger')

    logger.info("Rendering resend confirmation page.")
    return render_template('auth/resend_confirmation.html', form=form)
    

@auth_bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    """
    متد ویرایش پروفایل کاربر
    """
    logger.info(f'Profile endpoint accessed by user: {current_user.name}')
    form = ProfileForm()
    
    try:
        if request.method == 'POST':
            logger.info(f"POST request received for profile update by user: {current_user.name}")
            if form.validate_on_submit():
                if save_user_fields(current_user, form, ['name', 'email']):
                    logger.info(f"Profile updated successfully for user: {current_user.name}")
                    flash("Profile updated successfully!", "success")
                    return redirect(url_for('auth.dashboard'))
            if form.errors:
                logger.warning(f"Form validation errors: {form.errors}")
            return render_template('auth/profile.html', form=form)

        # مقداردهی اولیه به فرم
        form.name.data = current_user.name
        form.email.data = current_user.email
        logger.info(f"Rendering profile page for user: {current_user.name}")

        return render_template('auth/profile.html', form=form)

    except Exception as e:
        logger.critical(f"Unexpected error in profile route for user {current_user.name}: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return render_template('auth/profile.html', form=form)


@auth_bp.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    """
    متد تغییر رمز عبور
    """
    logger.info(f'Change password endpoint accessed by user: {current_user.name}')
    form = ChangePasswordForm(email=current_user.email)

    try:
        if request.method == 'POST':
            logger.info(f"POST request received for password change by user: {current_user.name}")
            if form.validate_on_submit():
                # بروزرسانی رمز عبور کاربر
                if save_user_fields(current_user, form, ['password']):
                    logger.info(f"Password changed successfully for user: {current_user.name}")
                    flash('Password changed successfully.', 'success')
                    return redirect(url_for('auth.dashboard'))

        if request.method == 'GET':
            # جلوگیری از تغییر رمز عبور در صورتی که کاربر با اکانت گوگل وارد شده باشد
            if current_user.auth_provider == "google":
                logger.info(f"Password change attempt for Google account by user: {current_user.name}")
                flash('You cannot change your password when you are logged in with your Google account.', 'info')
                return redirect(url_for('auth.dashboard'))

        if form.errors:
            # مدیریت خطاهای اعتبارسنجی فرم
            logger.warning(f"Form validation errors: {form.errors}")

    except Exception as e:
        # ثبت خطاهای غیرمنتظره
        logger.critical(f"Unexpected error in change_password route for user {current_user.name}: {str(e)}")
        flash('An unexpected error occurred. Please try again later.', 'danger')

    # رندر صفحه تغییر رمز عبور
    logger.info(f"Rendering change password page for user: {current_user.name}")
    return render_template('auth/change_password.html', form=form)


@auth_bp.route('/reset_password', methods=['GET', 'POST'])
def reset_password():
    """
    متد بازیابی رمز عبور
    """
    logger.info('Reset password endpoint accessed.')

    try:
        # اگر کاربر وارد سیستم شده باشد، او را به داشبورد هدایت می‌کنیم
        if current_user.is_authenticated:
            logger.info(f"User {current_user.name} is already authenticated. Redirecting to dashboard.")
            return redirect(url_for('auth.dashboard'))

        form = ResetPasswordForm()

        if request.method == 'POST':
            logger.info('POST request received for password reset.')
            
            if form.validate_on_submit():
                email = form.email.data
                logger.info(f"Password reset requested for email: {email}")
                
                user = User.get_by_email(email)

                if not user:
                    logger.warning(f"No user found with email: {email}")
                    flash("No user found with this email address.", "danger")
                    return redirect(url_for('auth.reset_password'))

                # ایجاد یا به‌روزرسانی توکن بازیابی رمز عبور
                user.set_token('password-reset')  # ایجاد توکن جدید
                db.session.commit()
                logger.info(f"Password reset token generated for user: {email}")

                # ارسال ایمیل بازیابی
                if send_reset_password_email(user):
                    logger.info(f"Password reset email sent to send email method")
                    flash("A reset link has been sent to your email.", "success")
                else:
                    logger.error(f"Failed to send password reset email to: {email}")
                    flash("Failed to send reset link. Please try again later.", "danger")

                return redirect(url_for('auth.login'))

            if form.errors:
                logger.warning(f"Form validation errors: {form.errors}")

        logger.info("Rendering reset password page.")
        return render_template('auth/reset_password.html', form=form)

    except Exception as e:
        logger.critical(f"Unexpected error in reset_password route: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('auth.reset_password'))


@auth_bp.route('/set_new_password/<token>', methods=['GET', 'POST'])
def set_new_password(token):
    """
    متد تنظیم رمز عبور جدید با استفاده از توکن بازیابی رمز عبور
    """
    logger.info(f'Set new password endpoint accessed with token: {token}')
    form = SetNewPasswordForm()

    try:
        if request.method == 'GET':
            logger.info('GET request received for set new password.')
            return render_template('auth/set_new_password.html', form=form, token=token)

        if request.method == 'POST':
            logger.info('POST request received for set new password.')
            
            if form.validate_on_submit():
                logger.info(f"Form validated successfully with token: {token}")
                
                user = User.get_by_token(token,'password_reset_token')

                if not user:
                    logger.warning(f"Invalid reset link or user not found for token: {token}")
                    flash("Invalid reset link or user not found.", "danger")
                    return redirect(url_for('auth.reset_password'))

                # بررسی اعتبار توکن
                if not user.verify_token(token,'password-reset'):
                    logger.warning(f"Reset link expired or invalid for token: {token}")
                    flash("Reset link expired or invalid.", "danger")
                    return redirect(url_for('auth.reset_password'))

                # تنظیم رمز جدید
                logger.info(f"Setting new password for user: {user.email}")
                user.set_password(form.password.data)
                user.password_reset_token = None
                db.session.commit()
                logger.info(f"Password updated successfully for user: {user.email}")

                flash("Your password has been updated. You can now login.", "success")
                return redirect(url_for('auth.login'))

            if form.errors:
                logger.warning(f"Form validation errors: {form.errors}")

        logger.info("Rendering set new password page.")
        return render_template('auth/set_new_password.html', form=form, token=token)

    except Exception as e:
        logger.critical(f"Unexpected error in set_new_password route: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('auth.reset_password'))


@auth_bp.route('/login/google')
def login_google():
    """
    متد ورود با استفاده از Google OAuth
    """
    logger.info('Google login endpoint accessed.')

    try:
        # ایجاد یک جلسه OAuth2 برای گوگل
        google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['email', 'profile'])
        authorization_url, state = google.authorization_url(
            authorization_base_url,
            access_type='offline',
            prompt='select_account'
        )
        logger.info('Google authorization URL generated.')

        # ذخیره حالت OAuth در سشن
        session['oauth_state'] = state
        logger.info(f"OAuth state stored in session: {state}")

        return redirect(authorization_url)

    except Exception as e:
        logger.critical(f"Unexpected error in login_google route: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('auth.login'))


@auth_bp.route('/login/google/callback')
def callback():
    """
    متد بازگشتی برای Google OAuth
    """
    logger.info('Google OAuth callback endpoint accessed.')

    try:
        # ایجاد یک جلسه OAuth2 برای گوگل
        google = OAuth2Session(client_id, state=session.get('oauth_state'), redirect_uri=redirect_uri)
        logger.info('OAuth session created for callback.')

        # دریافت توکن دسترسی
        token = google.fetch_token(
            token_url,
            client_secret=client_secret,
            authorization_response=request.url
        )
        logger.info('Access token fetched successfully.')

        # دریافت اطلاعات کاربر از گوگل
        user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()
        logger.info(f"User info retrieved from Google: {user_info}")

        # بررسی وجود کاربر در پایگاه داده
        user = User.query.filter_by(email=user_info['email']).first()
        if not user:
            logger.info(f"No user found for email: {user_info['email']}. Creating new user.")
            user = User(email=user_info['email'], name=user_info['name'], auth_provider="google")
            db.session.add(user)
            db.session.commit()
            logger.info(f"New user created with email: {user_info['email']}")

        # ورود کاربر
        login_user(user)
        logger.info(f"User {user.email} logged in successfully via Google OAuth.")

        return redirect(url_for('auth.dashboard'))

    except Exception as e:
        logger.critical(f"Unexpected error in Google OAuth callback: {str(e)}")
        flash("An unexpected error occurred during Google login. Please try again later.", "danger")
        return redirect(url_for('auth.login'))


@auth_bp.route('/dashboard')
@login_required
def dashboard():
    """
    متد نمایش داشبورد برای کاربر
    """
    logger.info(f"Dashboard endpoint accessed by user: {current_user.name}")

    try:
        # رندر صفحه داشبورد
        return render_template('dashboard.html')

    except Exception as e:
        logger.critical(f"Unexpected error in dashboard route for user {current_user.name}: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('auth.login'))


@auth_bp.route('/logout')
@login_required
def logout():
    """
    متد خروج کاربر از سیستم
    """
    logger.info(f"User {current_user.name} logged out.")

    try:
        # خروج کاربر
        logout_user()
        logger.info("User session cleared successfully.")
        flash("You have been logged out.", "info")

        return redirect(url_for('auth.login'))

    except Exception as e:
        logger.critical(f"Unexpected error during logout for user {current_user.name}: {str(e)}")
        flash("An unexpected error occurred during logout. Please try again later.", "danger")
        return redirect(url_for('auth.dashboard'))



def save_user_fields(user, form, fields):
    """
    ذخیره یا به‌روزرسانی فیلدهای مشخص‌شده برای کاربر با استفاده از متد مدل.
    """
    try:
        updates = {field: getattr(form, field).data for field in fields if hasattr(user, field) and hasattr(form, field)}
        if user.save_fields(updates):  # استفاده از متد `save_fields` در مدل
            logger.info(f"User {user.email} updated successfully.")
            return True
        else:
            logger.info(f"No changes made for user: {user.email}")
            return False

    except Exception as e:
        logger.error(f"Error updating user {getattr(user, 'email', 'Unknown')}: {str(e)}")
        return False

def send_confirmation_email(user):
    """
    ارسال ایمیل تایید برای کاربر
    """
    logger.info(f"Attempting to send confirmation email to user: {user.email}")

    try:
        if user.email and user.email_verification_token:
            logger.info(f"User {user.email} has a valid email and verification token.")

            # دریافت قالب ایمیل تایید
            email_verification_template = Notification.query.filter_by(name="Email Verification").first()
            if not email_verification_template:
                logger.error("Email verification template not found.")
                return False

            # ساخت لینک تایید
            confirm_url = url_for('auth.confirm_email', token=user.email_verification_token, _external=True)
            redisClient = RedisClient()
            email_body_data = {
                "name": user.name,
                "Confirm_url": confirm_url,
                "app_title": redisClient.get('app_title')
            }

            # پر کردن قالب ایمیل با داده‌های کاربر
            email_body = Template(email_verification_template.body).substitute(email_body_data)

            # ارسال ایمیل
            emailSender = EmailSender()
            emailSender.send_email(
                subject=email_verification_template.subject,
                recipients=[user.email],
                body="",
                html=email_body
            )
            logger.info(f"Confirmation email sent to {user.email}")
            return True

        logger.warning(f"User {user.email} is missing email or verification token.")
        return False

    except Exception as e:
        logger.critical(f"Failed to send confirmation email to {user.email}: {str(e)}")
        return False

def send_reset_password_email(user):
    """
    ارسال ایمیل بازیابی رمز عبور برای کاربر
    """
    logger.info(f"Attempting to send password reset email to user: {user.email}")

    try:
        if user.email and user.password_reset_token:
            logger.info(f"User {user.email} has a valid email and password reset token.")

            # دریافت قالب ایمیل بازیابی رمز عبور
            email_password_reset_template = Notification.query.filter_by(name="Reset Password").first()
            if not email_password_reset_template:
                logger.error("Password reset email template not found.")
                return False

            # ساخت لینک بازنشانی رمز عبور
            confirm_url = url_for('auth.set_new_password', token=user.password_reset_token, _external=True)
            redisClient = RedisClient()
            email_body_data = {
                "name": user.name,
                "Reset_url": confirm_url,
                "app_title": redisClient.get('app_title')
            }

            # پر کردن قالب ایمیل با داده‌های کاربر
            email_body = Template(email_password_reset_template.body).substitute(email_body_data)

            # ارسال ایمیل
            emailSender = EmailSender()
            emailSender.send_email(
                subject=email_password_reset_template.subject,
                recipients=[user.email],
                body="",
                html=email_body
            )
            logger.info(f"Password reset email sent to {user.email}")
            return True

        logger.warning(f"User {user.email} is missing email or password reset token.")
        return False

    except Exception as e:
        logger.critical(f"Failed to send password reset email to {user.email}: {str(e)}")
        return False
