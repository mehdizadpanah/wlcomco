from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, IntegerField
from wtforms.validators import DataRequired, Length, Optional
from ..lazy_title import LazyTitle

class TranslationForm(FlaskForm):
    key = StringField(LazyTitle('Key'), validators=[
        DataRequired(),
        Length(max=255)
    ])
    context = StringField(LazyTitle('Context'), validators=[
        Length(max=100)
    ])
    source_type = SelectField(LazyTitle('Source Type'), choices=[
        ('database', 'Database'),
        ('title', 'Title'),
        ('notice', 'Notice'),
        ('template', 'Template'),
        ('validation','Validation')
    ], validators=[DataRequired()])
    progress = IntegerField(LazyTitle('Progress'), validators=[Optional()])
