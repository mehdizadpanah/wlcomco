from flask_wtf import FlaskForm
from wtforms import PasswordField,StringField,SubmitField
from wtforms.validators import DataRequired,Length,EqualTo,Email,ValidationError
from ...models import User
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle
from ...services import get_translation

class ChangePasswordForm(FlaskForm):
    email = StringField("Email",render_kw={'readonly': True})

    old_password = PasswordField(LazyTitle("Old Password"),validators=[LazyValidator(DataRequired(), 'required')])

    password = PasswordField(LazyTitle("Password"),validators=[LazyValidator(DataRequired(), 'required'),
                                                    LazyValidator(Length(min=6), 'min_length')])
    
    confirm_password = PasswordField (LazyTitle("Confirm password"),validators=[LazyValidator(DataRequired(), 'required'),
                                                                     LazyValidator(EqualTo('password'),'password_match')])

    submit = SubmitField('change_password')

    def validate_old_password(self,old_password):
        self.find_user()
        if self.user:
            if not self.user.check_password(old_password.data):
                raise ValidationError (get_translation('','Old password is not correct.'))
        

    def find_user(self):
        self.user = User.query.filter_by(email=self.email.data).first()
