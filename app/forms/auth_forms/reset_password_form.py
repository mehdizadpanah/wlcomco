# app/forms/auth_forms/reset_password_form.py
from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Email
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle


class ResetPasswordForm(FlaskForm):
    email = StringField(LazyTitle('Email'), validators=[LazyValidator(DataRequired(),'required'),
                                             LazyValidator(Email(),'email')])

    
