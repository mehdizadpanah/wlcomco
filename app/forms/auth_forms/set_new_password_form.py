from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo,Length

class SetNewPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired(),Length(min=6)])
    confirm_password = PasswordField(
        'Confirm Password',
        validators=[
            DataRequired(),
            EqualTo('password', message='Passwords must match.')
        ]
    )
