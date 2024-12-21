from flask_wtf import FlaskForm
from ...models import User
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo,length,ValidationError

class SignupForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), 
    Email()])

    name = StringField('Name', validators=[DataRequired(),
    length(min=3,max=40)])

    password = PasswordField('Password', validators=[DataRequired()
    ,length(min=6)])

    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            raise ValidationError("This email is already registered.")
        

