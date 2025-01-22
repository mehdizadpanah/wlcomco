from .login_form import LoginForm
from .signup_form import SignupForm
from .profile_form import ProfileForm
from .change_password_form import ChangePasswordForm
from .resend_confirmation_form import ResendConfirmationForm
from .reset_password_form import ResetPasswordForm
from .set_new_password_form import SetNewPasswordForm

# لیستی از فرم‌ها برای استفاده در کل پروژه
__all__ = ['LoginForm', 'SignupForm','ProfileForm','ChangePasswordForm','ResendConfirmationForm','ResetPasswordForm',
           'SetNewPasswordForm']
