from flask_wtf import FlaskForm
from wtforms.widgets import PasswordInput
from wtforms import StringField, IntegerField, PasswordField,SelectField
from wtforms.validators import DataRequired,Email
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle

class SMTPSettingsForm(FlaskForm):
    smtp_host = StringField(LazyTitle('SMTP Host'), validators=[LazyValidator(DataRequired(), 'required')])
    smtp_port = IntegerField(LazyTitle('SMTP Port'), validators=[LazyValidator(DataRequired(), 'required')])
    smtp_username = StringField(LazyTitle('SMTP Username'), validators=[LazyValidator(DataRequired(), 'required')])
    smtp_password = PasswordField(LazyTitle('SMTP Password'), validators=[LazyValidator(DataRequired(), 'required')], widget=PasswordInput(hide_value=False))
    smtp_from = StringField(LazyTitle('SMTP From'), validators=[LazyValidator(DataRequired(), 'required')
                            ,LazyValidator(Email(), 'email')])

    smtp_security = SelectField(LazyTitle('SMTP Security'), 
                            choices=[('None', 'No Security'), 
                                     ('SSL', 'SSL Encryption'), 
                                     ('TLS', 'TLS Encryption')], 
                            validators=[LazyValidator(DataRequired(), 'required')])

