from flask_wtf import FlaskForm
from wtforms.widgets import PasswordInput
from wtforms import StringField, IntegerField, PasswordField,SelectField
from wtforms.validators import DataRequired,Email

class ChannelSettingsForm(FlaskForm):
    smtp_host = StringField('SMTP Host', validators=[DataRequired()])
    smtp_port = IntegerField('SMTP Port', validators=[DataRequired()])
    smtp_username = StringField('SMTP Username', validators=[DataRequired()])
    smtp_password = PasswordField('SMTP Password', validators=[DataRequired()], widget=PasswordInput(hide_value=False))
    smtp_from = StringField('SMTP From', validators=[DataRequired(),Email()])
    smtp_security = SelectField('SMTP Security', 
                            choices=[('None', 'No Security'), 
                                     ('SSL', 'SSL Encryption'), 
                                     ('TLS', 'TLS Encryption')], 
                            validators=[DataRequired()])
    

