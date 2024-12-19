from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo,length

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), 
    Email(message="Enter a valid email address.")])

    name = StringField('Name', validators=[DataRequired(),
    length(min=3,message="Name must be at least 2 characters long.")])

    password = PasswordField('Password', validators=[DataRequired()
    ,length(min=6,message="Password must be at least 6 characters long.")])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Sign Up')
