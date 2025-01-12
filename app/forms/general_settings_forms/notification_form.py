from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired

class NotificationForm(FlaskForm):
    name = StringField('Template Name', validators=[DataRequired()])
    send_via = SelectField('Send Via', choices=[('email', 'Email'), ('sms', 'SMS')], validators=[DataRequired()])
    content_type = SelectField('Content Type', choices=[('text', 'Text'), ('html', 'HTML')], validators=[DataRequired()])
    description = TextAreaField('Description')
    body = TextAreaField('Template Content', validators=[DataRequired()])
    subject = StringField('Subject', validators=[DataRequired()])
