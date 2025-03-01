from ..extensions import db, DBUtils, get_logger, UnitUtils
from .mixins import TimestampMixin, UserTrackingMixin
from sqlalchemy.dialects.mysql import BINARY
from .translation_value import TranslationValue
from .language import Language


logger = get_logger('model')

class Translation(db.Model, TimestampMixin, UserTrackingMixin):
    __tablename__ = 'translation'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=DBUtils.generate_uuid)
    key = db.Column(db.Text, unique=True, nullable=False)  # کلید یکتای متن مثل 'dashboard.title'
    context = db.Column(db.Text, nullable=True)  # زمینه یا ماژول مرتبط
    source_type = db.Column(db.String(50), default='file')  # 'file' یا 'database'

    def __repr__(self):
        return f"<Translation {self.key}>"
    
    def get_id_hex(self):
        """
        تبدیل شناسه باینری (UUID) به رشته هگز
        """
        try:
            return UnitUtils.bytes_to_hex(self.id)
        except Exception as e:
            logger.error(f"Error converting ID to hex: {str(e)}")
            return None

    def get_completed_languages(self):
        try:
            languages = Language.query.filter(Language.code != 'en').all()
            completed_count = 0
            for language in languages:
                value = TranslationValue.query.filter_by(
                    translation_id=self.id,
                    language_id=language.id
                ).first()
                if value and value.value:
                    completed_count += 1
            return completed_count
        except Exception as e:
            logger.error(f"Error fetching completed languages for translation ID {self.id}: {str(e)}")
            return 0

    def get_value_for_language(self, language_id):
        """
        دریافت مقدار ترجمه برای یک زبان خاص
        """
        try:
            translation_value = TranslationValue.query.filter_by(
                translation_id=self.id,
                language_id=language_id
            ).first()
            
            if translation_value:
                return translation_value.value
            return None
        except Exception as e:
            logger.error(f"Error fetching translation value for language ID {language_id}: {str(e)}")
            return None

    @classmethod
    def get_by_key(cls, key):
        """
        جستجوی ترجمه بر اساس کلید.
        """
        logger.info(f"Fetching translation with key: {key}")
        try:
            translation = cls.query.filter_by(key=key).first()
            if translation:
                logger.info(f"Translation with key '{key}' found.")
            else:
                logger.info(f"Translation with key '{key}' not found.")
            return translation
        except Exception as e:
            logger.error(f"Error occurred while fetching translation key '{key}': {str(e)}")
            return None

    @classmethod
    def get_by_id(cls, translation_id):
        logger.info(f"Fetching translation with ID: {translation_id}")
        try:
            return cls.query.get(translation_id)
        except Exception as e:
            logger.error(f"Error fetching translation ID '{translation_id}': {str(e)}")
            return None

    @classmethod
    def get_all(cls):
        logger.info("Fetching all translations.")
        try:
            return cls.query.order_by(cls.source_type).all()
        except Exception as e:
            logger.error(f"Error fetching translations: {str(e)}")
            return []

    def save(self, new_context=None):
        """
        ذخیره یا به‌روزرسانی ترجمه در دیتابیس.
        اگر `new_context` ارسال شود، به لیست کانتکست‌های موجود اضافه می‌شود.
        """
        logger.info(f"Saving translation with key: {self.key}")
        try:
            # بررسی وجود رکورد در دیتابیس
            existing_translation = Translation.query.filter_by(key=self.key).first()

            if existing_translation:
                # اضافه کردن کانتکست جدید به کانتکست‌های قبلی (در صورت وجود)
                existing_contexts = existing_translation.context.split(',') if existing_translation.context else []
                if new_context and new_context not in existing_contexts:
                    existing_contexts.append(new_context)
                    existing_translation.context = ','.join(existing_contexts)
                    logger.info(f"Context '{new_context}' added to key '{self.key}'")

                db.session.commit()
                logger.info(f"Translation key '{self.key}' updated successfully.")
                return True

            else:
                # اگر ترجمه وجود ندارد، رکورد جدید ایجاد کن
                if new_context:
                    self.context = new_context  # تغییر از contexts به context
                if not self.id:
                    self.id = DBUtils.generate_uuid()  # تولید ID در صورت عدم وجود

                if db.session.object_session(self) is None:
                    db.session.add(self)

                db.session.commit()
                logger.info(f"Translation key '{self.key}' saved successfully.")
                return True

        except Exception as e:
            logger.error(f"Error occurred while saving translation key '{self.key}': {str(e)}")
            db.session.rollback()
            return False

    @classmethod
    def delete(cls, translation_id):
        """
        حذف ترجمه بر اساس ID به همراه تمام مقادیر ترجمه مرتبط (TranslationValues)
        """
        try:
            translation = cls.query.get(translation_id)
            if translation:
                # حذف تمام مقادیر ترجمه مرتبط
                TranslationValue.query.filter_by(translation_id=translation_id).delete()

                # حذف خود ترجمه
                db.session.delete(translation)
                db.session.commit()

                logger.info(f"Translation '{translation.key}' and related translation values deleted successfully.")
                return True
            else:
                logger.warning(f"Translation with ID '{translation_id}' not found.")
                return False

        except Exception as e:
            logger.error(f"Error deleting translation: {str(e)}")
            db.session.rollback()
            return False
