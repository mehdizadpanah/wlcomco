from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle


class ResendConfirmationForm(FlaskForm):
    email = StringField(LazyTitle('Email address'), validators=[LazyValidator(DataRequired(), 'required'),
                                                     LazyValidator(Email(),'email')])