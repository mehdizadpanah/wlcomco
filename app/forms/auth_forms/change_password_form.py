from flask_wtf import FlaskForm
from wtforms import PasswordField,StringField,SubmitField
from wtforms.validators import DataRequired,Length,EqualTo,Email,ValidationError
from ...models import User

class ChangePasswordForm(FlaskForm):
    email = StringField("Email",render_kw={'readonly': True},validators=[DataRequired(),Email()])

    old_password = PasswordField("Old Password",validators=[DataRequired()])

    password = PasswordField("Password",validators=[DataRequired(),Length(min=6)])
    
    confirm_password = PasswordField ("Confirm password",validators=[DataRequired(),
    EqualTo('password', message='Password must match')])

    submit = SubmitField('change_password')

    def validate_old_password(self,old_password):
        self.find_user()
        if self.user:
            if not self.user.check_password(old_password.data):
                raise ValidationError ("Old password is not correct.")
        

    def find_user(self):
        self.user = User.query.filter_by(email=self.email.data).first()
