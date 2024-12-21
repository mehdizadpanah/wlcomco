from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField
from wtforms.validators import length,DataRequired

class ProfileForm(FlaskForm):
    email = StringField("Email", render_kw={'readonly': True})
    name = StringField("Name",validators=[DataRequired(),length(min=3,max=40)])