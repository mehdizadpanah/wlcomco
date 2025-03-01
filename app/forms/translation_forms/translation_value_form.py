from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired, Length

class TranslationValueForm(FlaskForm):
    translation_id = StringField('Translation ID', validators=[
        DataRequired(),
        Length(max=36)  # UUID به صورت رشته
    ])
    language_id = StringField('Language ID', validators=[
        DataRequired(),
        Length(max=36)  # UUID به صورت رشته
    ])
    value = StringField('Value', validators=[
        DataRequired()
    ])
