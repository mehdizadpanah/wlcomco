from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email

class ResendConfirmationForm(FlaskForm):
    email = StringField('Email address', validators=[DataRequired(), Email()])