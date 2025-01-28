from flask_wtf import FlaskForm
from wtforms.widgets import PasswordInput
from wtforms import StringField, IntegerField, PasswordField,SelectField
from wtforms.validators import DataRequired,NumberRange

class SettingsForm(FlaskForm):
    app_title = StringField ('Application Title', validators=[DataRequired()])
    logging_level = SelectField ('Logging Level',
                                 choices=[
                                    ('NOTSET', 'Not Set'),
                                    ('DEBUG', 'Debug'),
                                    ('INFO', 'Info'),
                                    ('WARNING', 'Warning'),
                                    ('ERROR', 'Error'),
                                    ('CRITICAL', 'Critical')
                                ],default='WARNING')
    logging_file_retention = IntegerField ('Logging file retention',validators=[DataRequired(),NumberRange(min=1,max=10)] )
    logging_file_size = IntegerField ('Logging maximume file size(MB)',validators=[DataRequired(),NumberRange(min=1,max=300)])


