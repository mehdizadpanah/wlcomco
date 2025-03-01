from flask_wtf import FlaskForm
from wtforms import PasswordField
from wtforms.validators import DataRequired, EqualTo,Length
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle


class SetNewPasswordForm(FlaskForm):
    password = PasswordField(LazyTitle('New Password'), validators=[LazyValidator(DataRequired(),'required'),
                                                         LazyValidator(Length(min=6),'')])
    confirm_password = PasswordField(LazyTitle('Confirm Password'),validators=[LazyValidator(DataRequired(),'required'),
                                                                    EqualTo('password','password_match')])
