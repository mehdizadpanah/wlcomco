from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField,BooleanField
from wtforms.validators import DataRequired, Email
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle


class LoginForm(FlaskForm):
    email = StringField(LazyTitle('Email address'), validators=[LazyValidator(DataRequired(), 'required')
                                                     ,LazyValidator(Email(),'email')])
    password = PasswordField(LazyTitle('Password'), validators=[LazyValidator(DataRequired(), 'required')])
    remember_me = BooleanField(LazyTitle('Remember Me'))

    submit = SubmitField('Login')


