from ..extensions import db,DBUtils,get_logger,UnitUtils
from .mixins import TimestampMixin, UserTrackingMixin
from sqlalchemy.dialects.mysql import BINARY

logger = get_logger('model')

class TranslationValue(db.Model,TimestampMixin, UserTrackingMixin):
    __tablename__ = 'translation_value'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=DBUtils.generate_uuid)
    translation_id = db.Column(BINARY(16), db.ForeignKey('translation.id'), nullable=False)
    language_id = db.Column(BINARY(16), db.ForeignKey('language.id'), nullable=False)
    value = db.Column(db.Text, nullable=False)  # متن ترجمه‌شده

    # روابط
    translation = db.relationship('Translation', backref=db.backref('values', lazy=True))
    language = db.relationship('Language', backref=db.backref('values', lazy=True))

    def __repr__(self):
        return f"<TranslationValue lang={self.language_id} key={self.translation_id}>"


    @classmethod
    def get_by_translation_and_language(cls, translation_id, language_id):
        """
        دریافت مقدار ترجمه بر اساس شناسه ترجمه و زبان.
        """
        try:
            # تبدیل شناسه‌های باینری به هگز برای ثبت در لاگ
            translation_id_hex = UnitUtils.bytes_to_hex(translation_id) 
            language_id_hex = UnitUtils.bytes_to_hex(language_id) 

            logger.info(f"Fetching translation value for translation_id: {translation_id_hex}, language_id: {language_id_hex}")

            translation_value = cls.query.filter_by(translation_id=translation_id, language_id=language_id).first()

            if translation_value:
                logger.info("Translation value found in database.")
            else:
                logger.warning("Translation value not found in database.")

            return translation_value

        except Exception as e:
            logger.error(f"Error fetching translation value: {str(e)}")
            return None

    # def save(self):
    #     """
    #     ذخیره یا به‌روزرسانی مقدار ترجمه.
    #     """
    #     logger.info(f"Saving translation value for translation_id: {self.translation_id}, language_id: {self.language_id}")
    #     try:
    #         if db.session.object_session(self) is None:
    #             self = db.session.merge(self)
    #             self.logger.info("Translation value merged into session.")

    #         db.session.commit()
    #         logger.info("Translation value saved successfully.")
    #         return True
    #     except Exception as e:
    #         logger.error(f"Error saving translation value: {str(e)}")
    #         db.session.rollback()
    #         return False

    @classmethod
    def create(cls, translation_id, language_id, value):
        logger.info(f"Creating translation value for translation_id: {translation_id}, language_id: {language_id}")
        try:
            new_value = cls(translation_id=translation_id, language_id=language_id, value=value)
            db.session.add(new_value)
            db.session.commit()
            return new_value
        except Exception as e:
            logger.error(f"Error creating translation value: {str(e)}")
            db.session.rollback()
            return None

    def update_value(self, new_value):
        logger.info(f"Updating translation value ID: {self.id}")
        try:
            if not new_value.strip():  # بررسی خالی بودن مقدار جدید
                logger.info(f"Empty translation detected for ID: {self.id}. Deleting record...")
                db.session.delete(self)
                db.session.commit()
                logger.info("Translation record deleted successfully.")
                return True

            # اگر مقدار جدید خالی نیست، به‌روزرسانی انجام شود
            self.value = new_value
            db.session.commit()
            logger.info("Translation value updated successfully.")
            return True

        except Exception as e:
            logger.error(f"Error updating translation value: {str(e)}")
            db.session.rollback()
            return False
        
    @classmethod
    def delete_by_language(cls, language_id):
        """
        حذف تمام ترجمه‌های مرتبط با یک زبان خاص
        """
        try:
            translations_to_delete = cls.query.filter_by(language_id=language_id).all()
            count = len(translations_to_delete)

            for translation in translations_to_delete:
                db.session.delete(translation)

            db.session.commit()
            logger.info(f"Deleted {count} translation values for language ID {UnitUtils.bytes_to_hex(language_id)}.")
            return count

        except Exception as e:
            logger.error(f"Error deleting translations for language ID {language_id}: {str(e)}")
            db.session.rollback()
            return 0
