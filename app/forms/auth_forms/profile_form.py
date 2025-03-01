from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, SelectField
from wtforms.validators import Length, DataRequired
from app.models.language import Language  # اطمینان از ایمپورت مدل Language
from app.extensions import UnitUtils  # برای تبدیل شناسه باینری به هگز
from ..lazy_validator import LazyValidator
from ..lazy_title import LazyTitle


class ProfileForm(FlaskForm):
    email = StringField(LazyTitle("Email"), render_kw={'readonly': True})
    
    name = StringField(LazyTitle("Name"), validators=[LazyValidator(DataRequired(), 'required'),
                                           LazyValidator(Length(min=3, max=40),'length')])
    # فیلد انتخاب زبان
    language = SelectField(LazyTitle("Preferred Language"), coerce=str)  # تبدیل مقادیر باینری به هگز (رشته)

    submit = SubmitField(LazyTitle("Save Changes"))

    def __init__(self, *args, **kwargs):
        super(ProfileForm, self).__init__(*args, **kwargs)
        
        # گزینه پیش‌فرض برای استفاده از زبان سیستم
        self.language.choices = [('', 'Use System Default')]

        # اضافه کردن زبان‌های فعال به لیست انتخاب
        active_languages = Language.query.filter_by(is_active=True).all()
        for lang in active_languages:
            self.language.choices.append((UnitUtils.bytes_to_hex(lang.id), lang.name))
