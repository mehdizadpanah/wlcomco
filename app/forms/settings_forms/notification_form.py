from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SelectField
from wtforms.validators import DataRequired
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle

class NotificationForm(FlaskForm):
    name = StringField(LazyTitle('Template Name'), validators=[LazyValidator(DataRequired(), 'required')])
    send_via = SelectField(LazyTitle('Send Via'), choices=[('email', 'Email'), ('sms', 'SMS')], 
                           validators=[LazyValidator(DataRequired(), 'required')])
    content_type = SelectField(LazyTitle('Content Type'), choices=[('text', 'Text'), ('html', 'HTML')], 
                            validators=[LazyValidator(DataRequired(), 'required')])
    description = TextAreaField(LazyTitle('Description'))
    body = TextAreaField(LazyTitle('Template Content'), validators=[LazyValidator(DataRequired(), 'required')])
    subject = StringField(LazyTitle('Subject'), validators=[LazyValidator(DataRequired(), 'required')])
