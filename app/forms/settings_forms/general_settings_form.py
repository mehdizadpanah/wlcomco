from flask_wtf import FlaskForm
from wtforms.widgets import PasswordInput
from wtforms import StringField, IntegerField, PasswordField,SelectField
from wtforms.validators import DataRequired,NumberRange
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle

class GeneralSettingsForm(FlaskForm):
    app_title = StringField (LazyTitle('Application title'), validators=[LazyValidator(DataRequired(), 'required')])
    logging_level = SelectField (LazyTitle('Logging level'),
                                 choices=[
                                    ('NOTSET', 'Not Set'),
                                    ('DEBUG', 'Debug'),
                                    ('INFO', 'Info'),
                                    ('WARNING', 'Warning'),
                                    ('ERROR', 'Error'),
                                    ('CRITICAL', 'Critical')
                                ],default='WARNING')
    logging_file_retention = IntegerField (LazyTitle('Logging file retention'),validators=[LazyValidator(DataRequired(), 'required'),
                                                                    LazyValidator(NumberRange(min=1,max=10), 'number_range')])
    logging_file_size = IntegerField (LazyTitle('Logging maximume file size(MB)'),validators=[LazyValidator(DataRequired(), 'required'),
                                                                    LazyValidator(NumberRange(min=1,max=10), 'number_range')])

