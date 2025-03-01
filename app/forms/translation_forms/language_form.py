from flask_wtf import FlaskForm
from wtforms import StringField, BooleanField,FileField
from wtforms.validators import DataRequired, Length,URL,Optional
from flask_wtf.file import FileAllowed
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle


class LanguageForm(FlaskForm):
    code = StringField(LazyTitle('Code'), validators=[LazyValidator(DataRequired(),'required'),
                                           LazyValidator(Length(max=10),'max_value')])
    name = StringField(LazyTitle('Name'), validators=[LazyValidator(DataRequired(),'required'),
                                           LazyValidator(Length(max=50),'max_value')])
    flag_path = StringField(LazyTitle('Flag'), validators=[Optional(), Length(max=255)])  # مسیر پرچم در دیتابیس
    flag_file = FileField(LazyTitle('Upload Flag'), validators=[Optional(), FileAllowed(['png', 'jpg', 'jpeg'], 'Images only!')])  # آپلود پرچم
    is_active = BooleanField(LazyTitle('Status'), default=True)
    default = BooleanField(LazyTitle('Default'), default=False)  # تعیین زبان پیش‌فرض
    rtl = BooleanField(LazyTitle('Right to left'), default=False)