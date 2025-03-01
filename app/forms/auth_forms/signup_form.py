from flask_wtf import FlaskForm
from ...models import User
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo,length,ValidationError
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle

from ...services import get_translation

class SignupForm(FlaskForm):
    email = StringField(LazyTitle('Email'), validators=[LazyValidator(DataRequired(),'required'), 
                                             LazyValidator(Email(),'email')])

    name = StringField(LazyTitle('Name'), validators=[LazyValidator(DataRequired(),'required'),
                                           LazyValidator(length(min=3,max=40),'length')])

    password = PasswordField(LazyTitle('Password'), validators=[LazyValidator(DataRequired(),'required'),
                                                     LazyValidator(length(min=6),'min_value')])

    confirm_password = PasswordField(LazyTitle('Confirm Password'), validators=[LazyValidator(DataRequired(), 'required'),
                                                                     LazyValidator(EqualTo('password'),'password_match')])
    
    submit = SubmitField('Sign Up')

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first():
            # raise ValidationError("This email is already registered.")
            raise ValidationError(get_translation('','This email is already registered.'))

        

