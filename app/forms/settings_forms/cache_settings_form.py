from flask_wtf import FlaskForm
from wtforms import HiddenField, StringField, IntegerField, PasswordField, SubmitField,TextAreaField
from wtforms.validators import DataRequired, Length, Optional
from app.extensions import UnitUtils
from app.models.cache_server import CacheServer
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle
from wtforms.widgets import PasswordInput


class CacheServerForm(FlaskForm):
    # در حالت ویرایش، مقدار شناسه (UUID) به صورت هگز در این فیلد پنهان قرار می‌گیرد
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
        validators=[
            LazyValidator(DataRequired(), 'required')
        ]
    )
    username = StringField(
        LazyTitle("Username"), 
        validators=[
            LazyValidator(Optional(), 'optional'),
            LazyValidator(Length(max=255), 'length')
        ]
    )
    password = PasswordField(
        LazyTitle("Password"), 
        validators=[
            LazyValidator(DataRequired(), 'required'),
            LazyValidator(Length(max=255), 'length')
        ],widget=PasswordInput(hide_value=False)
    )
    db_index = IntegerField(
        LazyTitle("DB Index"), 
        validators=[
            LazyValidator(DataRequired(), 'required')
        ]
    )

    description = TextAreaField(
        LazyTitle("Description"),
        validators=[
            LazyValidator(Optional(), 'optional')
        ],
        render_kw={"rows": 3}  # تنظیم ارتفاع textarea
    )

    submit = SubmitField(LazyTitle("Save"))

    def __init__(self, *args, **kwargs):
        super(CacheServerForm, self).__init__(*args, **kwargs)
        # در صورت نیاز می‌توانید در اینجا داده‌های پویا را بارگذاری کنید
        # یا مقادیر پیش‌فرض فیلدها را از جایی بخوانید.
