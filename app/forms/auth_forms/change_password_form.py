from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired,Length,EqualTo

class ChangePasswordForm(FlaskForm):
    password = PasswordField("Password",validators=(DataRequired(),Length(min=6)))
    
    confirm_password = PasswordField ("Confirm password",validators=(DataRequired(),
    EqualTo('password', message='Password must match')))