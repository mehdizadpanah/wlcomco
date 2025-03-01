from ..extensions import db, get_logger, UnitUtils,DBUtils,flask_extensions
from sqlalchemy.dialects.mysql import BINARY
from .translation_value import TranslationValue
from app.models import User  # ایمپورت مدل کاربر در صورت نیاز


logger = get_logger('model')

class Language(db.Model):
    __tablename__ = 'language'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=DBUtils.generate_uuid())
    code = db.Column(db.String(10), unique=True, nullable=False)  # مثل 'en', 'fa'
    name = db.Column(db.String(50), nullable=False)  # مثل 'English', 'فارسی'
    is_active = db.Column(db.Boolean, default=True)  # وضعیت فعال/غیرفعال بودن
    flag = db.Column(db.String(255), nullable=True)  # مسیر پرچم زبان (فعلاً بدون آپلود فایل)
    default = db.Column(db.Boolean, default=False)  # برای زبان پیش‌فرض
    rtl = db.Column(db.Boolean, default=False)  # تعیین جهت راست به چپ

    def __repr__(self):
        return f"<Language {self.code}: {self.name}>"

    def get_id_hex(self):
        """دریافت ID به صورت هگز برای ارتباط با UI"""
        return UnitUtils.bytes_to_hex(self.id)

    def save(self, original_data=None):
        """افزودن یا به‌روزرسانی زبان و ثبت تغییرات در لاگ"""
        logger.info(f"Saving language: {self.code} - {self.name}")
        try:
            if original_data:
                # بررسی تغییرات
                for field, new_value in vars(self).items():
                    old_value = original_data.get(field)
                    if old_value != new_value:
                        logger.info(
                            f"Field '{field}' changed for language '{self.code}': from '{old_value}' to '{new_value}'"
                        )

            # ذخیره در پایگاه داده
            if db.session.object_session(self) is None:
                self = db.session.merge(self)
                logger.info(f"Language {self.code} merged into session.")

            db.session.commit()
            logger.info(f"Language saved successfully: {self.code} - {self.name}")
            return True
        except Exception as e:
            logger.error(f"Error saving language {self.code}: {str(e)}")
            db.session.rollback()
            return False

    @classmethod
    def get_all(cls):
        """دریافت لیست تمام زبان‌ها"""
        try:
            logger.info("Fetching all languages from the database.")
            return cls.query.order_by(cls.name.asc()).all()
        except Exception as e:
            logger.error(f"Error fetching languages: {e}")
            return []

    @classmethod
    def get_by_id(cls, lang_id):
        """دریافت یک زبان بر اساس ID"""
        try:
            logger.info(f"Fetching language with ID: {UnitUtils.bytes_to_hex(lang_id)}")
            return cls.query.get(lang_id)
        except Exception as e:
            logger.error(f"Error fetching language by ID: {e}")
            return None

    @classmethod
    def delete(cls, lang_id):
        """
        حذف زبان از دیتابیس به همراه تمام ترجمه‌های مرتبط و به‌روزرسانی کاربران.
        """
        try:
            language = cls.get_by_id(lang_id)
            if not language:
                logger.warning(f"Language with ID {UnitUtils.bytes_to_hex(lang_id)} not found.")
                return False, "Language not found."

            # اگر زبان پیش‌فرض باشد، اجازه حذف ندهید
            if language.default:
                logger.warning(f"Cannot delete the default language: {language.code}. Please set another language as default before deletion.")
                return False, "Cannot delete the default language. Please set another language as default before deletion."

            # پیدا کردن زبان پیش‌فرض
            default_language = cls.query.filter_by(default=True).first()
            if not default_language:
                logger.error("Default language not found. Cannot proceed with deletion.")
                return False, "Default language not found. Cannot proceed with deletion."

            # به‌روزرسانی کاربران وابسته به این زبان
            from app.models import User  # ایمپورت مدل کاربر در صورت نیاز
            affected_users = User.query.filter_by(language_id=lang_id).all()
            for user in affected_users:
                user.language_id = default_language.id
                logger.info(f"Updated user {user.email} to default language {default_language.code}")

            # حذف تمام ترجمه‌های مرتبط با این زبان
            from app.models import TranslationValue  # ایمپورت مدل ترجمه
            deleted_translations = TranslationValue.delete_by_language(lang_id)

            # حذف زبان
            db.session.delete(language)
            db.session.commit()

            logger.info(f"Language deleted: {language.code} - {language.name} with {deleted_translations} translations.")
            return True, "Language deleted successfully."

        except Exception as e:
            logger.error(f"Error deleting language '{language.name}' and its translations: {str(e)}")
            db.session.rollback()
            return False, "An error occurred while deleting the language."

    @classmethod
    def toggle_status(cls, lang_id):
        """فعال/غیرفعال کردن زبان"""
        try:
            language = cls.get_by_id(lang_id)
            if not language:
                logger.warning(f"Language with ID {UnitUtils.bytes_to_hex(lang_id)} not found.")
                return False

            language.is_active = not language.is_active
            db.session.commit()
            logger.info(f"Language {language.code} status changed to: {'Active' if language.is_active else 'Inactive'}")
            return language.is_active
        except Exception as e:
            logger.error(f"Error toggling language status: {e}")
            db.session.rollback()
            return False

    @classmethod
    def get_by_code(cls, lang_code):
        """دریافت یک زبان بر اساس ID"""
        try:
            logger.info(f"Fetching language with code: {lang_code}")
            return cls.query.filter_by(code=lang_code).first()
        except Exception as e:
            logger.error(f"Error fetching language by ID: {e}")
            return None

    @classmethod
    def set_default(cls, lang_id):
        """
        تنظیم یک زبان به‌عنوان زبان پیش‌فرض.
        فقط یک زبان می‌تواند مقدار default=True داشته باشد.
        """
        try:
            logger.info(f"Setting default language for ID: {UnitUtils.bytes_to_hex(lang_id)}")

            # غیرفعال کردن پیش‌فرض برای تمام زبان‌ها
            cls.query.update({cls.default: False})
            db.session.commit()

            # فعال کردن پیش‌فرض برای زبان انتخاب‌شده
            language = cls.get_by_id(lang_id)
            if language:
                language.default = True
                db.session.commit()

                logger.info(f"Language '{language.name}' set as default.")
                return True
            else:
                logger.warning(f"Language with ID {UnitUtils.bytes_to_hex(lang_id)} not found.")
                return False

        except Exception as e:
            logger.error(f"Error setting default language: {str(e)}")
            db.session.rollback()
            return False
