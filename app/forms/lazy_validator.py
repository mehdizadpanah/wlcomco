from wtforms.validators import (
    DataRequired, Email, Length, EqualTo, NumberRange, AnyOf, NoneOf, Regexp
)
from app.services import get_validation_error

# نمونه‌هایی از ولیدیتورهای سفارشی یا Flask-WTF که ممکن است در پروژه استفاده شوند:
class FileRequired:
    def __init__(self, message=None):
        self.message = message

    def __call__(self, form, field):
        if not field.data:
            raise ValueError(self.message)

class FileAllowed:
    def __init__(self, extensions, message=None):
        self.extensions = extensions
        self.message = message

    def __call__(self, form, field):
        pass

class FileSize:
    def __init__(self, max_size, message=None):
        self.max_size = max_size
        self.message = message

    def __call__(self, form, field):
        pass

class MultipleOf:
    def __init__(self, number, message=None):
        self.number = number
        self.message = message

    def __call__(self, form, field):
        pass

class MaxValue:
    def __init__(self, max_val, message=None):
        self.max_val = max_val
        self.message = message

    def __call__(self, form, field):
        pass

class MinValue:
    def __init__(self, min_val, message=None):
        self.min_val = min_val
        self.message = message

    def __call__(self, form, field):
        pass


class LazyValidator:
    """
    یک Wrapper عمومی برای ولیدیتورهای WTForms (یا سفارشی)
    که پیام خطا را به صورت lazy (در زمان اجرا) ترجمه می‌کند.
    """
    def __init__(self, validator, translation_key):
        """
        :param validator: شیء ولیدیتور (مثلاً DataRequired(), Length(min=6), Email(), ...)
        :param translation_key: کلید ترجمه‌ای که در دیکشنری validation_messages استفاده می‌شود.
        """
        self.validator = validator
        self.translation_key = translation_key

    def __call__(self, form, field):
        # در این دیکشنری، پارامترهای داینامیک را ذخیره می‌کنیم
        placeholders = {}

        # 1. Length => کلیدهای 'min_length'، 'max_length' یا 'length'
        if isinstance(self.validator, Length):
            placeholders['min'] = self.validator.min
            placeholders['max'] = self.validator.max

        # 2. EqualTo => کلید 'equal_to'
        elif isinstance(self.validator, EqualTo):
            placeholders['other_name'] = self.validator.fieldname

        # 3. NumberRange => کلید 'number_range'
        elif isinstance(self.validator, NumberRange):
            placeholders['min'] = self.validator.min
            placeholders['max'] = self.validator.max

        # 4. AnyOf => کلید 'any_of'
        elif isinstance(self.validator, AnyOf):
            placeholders['values'] = ', '.join(str(v) for v in self.validator.values)

        # 5. NoneOf => کلید 'none_of'
        elif isinstance(self.validator, NoneOf):
            placeholders['values'] = ', '.join(str(v) for v in self.validator.values)

        # 6. Regexp => کلید 'regexp'
        elif isinstance(self.validator, Regexp):
            placeholders['regex'] = self.validator.regex.pattern if self.validator.regex else ''

        # 7. فایل‌های سفارشی FileRequired => کلید 'file_required'
        elif isinstance(self.validator, FileRequired):
            pass

        # 8. FileAllowed => کلید 'file_allowed'
        elif isinstance(self.validator, FileAllowed):
            placeholders['extensions'] = ', '.join(self.validator.extensions)

        # 9. FileSize => کلید 'file_size'
        elif isinstance(self.validator, FileSize):
            placeholders['max_size'] = self.validator.max_size

        # 10. MultipleOf => کلید 'multiple_of'
        elif isinstance(self.validator, MultipleOf):
            placeholders['number'] = self.validator.number

        # 11. MaxValue => کلید 'max_value'
        elif isinstance(self.validator, MaxValue):
            placeholders['max'] = self.validator.max_val

        # 12. MinValue => کلید 'min_value'
        elif isinstance(self.validator, MinValue):
            placeholders['min'] = self.validator.min_val

        # در نهایت پیام خطا را ترجمه و جایگزین می‌کنیم
        self.validator.message = get_validation_error(self.translation_key, **placeholders)

        # اجرای ولیدیتور اصلی
        return self.validator(form, field)
