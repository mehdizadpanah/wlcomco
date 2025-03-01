from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, IntegerField, PasswordField, SelectField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Optional
from wtforms.widgets import PasswordInput
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle

class FileServerForm(FlaskForm):
    id = HiddenField(LazyTitle("ID"))

    name = StringField(
        LazyTitle("Name"),
        validators=[
            LazyValidator(DataRequired(), 'required'),
            LazyValidator(Length(min=3, max=100), 'length')
        ]
    )

    host = StringField(
        LazyTitle("Host"),
        validators=[
            LazyValidator(DataRequired(), 'required'),
            LazyValidator(Length(min=3, max=255), 'length')
        ]
    )

    port = IntegerField(
        LazyTitle("Port"),
        validators=[LazyValidator(Optional(), 'optional')]
    )

    storage_type = SelectField(
        LazyTitle("Storage Type"),
        choices=[('LOCAL', 'Local'), ('FTP', 'FTP'), ('SFTP', 'SFTP'), ('CLOUD', 'Cloud'), ('NFS', 'NFS')],
        validators=[LazyValidator(DataRequired(), 'required')]
    )

    path = StringField(
        LazyTitle("Storage Path"),
        validators=[LazyValidator(DataRequired(), 'required')]
    )

    username = StringField(
        LazyTitle("Username"),
        validators=[LazyValidator(Optional(), 'optional')]
    )

    password = PasswordField(
        LazyTitle("Password"),
        validators=[LazyValidator(Optional(), 'optional')],
        widget=PasswordInput(hide_value=False)
    )

    api_key = StringField(
        LazyTitle("API Key"),
        validators=[LazyValidator(Optional(), 'optional')]
    )

    is_active = BooleanField(LazyTitle("Is Active"), default=True)

    submit = SubmitField(LazyTitle("Save"))
