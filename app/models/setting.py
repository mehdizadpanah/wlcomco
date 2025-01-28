from ..extensions import db,RedisClient,Encryption,get_logger
import uuid
from sqlalchemy.dialects.mysql import BINARY


logger = get_logger('model')

def generate_uuid():
    """
    تولید یک مقدار باینری 16 بایتی (UUID نسخه 4).
    """
    return uuid.uuid4().bytes  # bytes شکل باینری UUID


class Setting(db.Model):
    __tablename__ = 'setting'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), nullable=False)
    value = db.Column(db.Text, nullable=False)  # نوع Text با پشتیبانی از یونیکد

    def __repr__(self):
        return f"<Setting {self.name}: {self.value}>"

    @classmethod
    def get_by_name(cls, name, default=None):
        """
        دریافت مقدار تنظیم بر اساس نام
        """
        logger.info(f"Fetching setting '{name}' with default value: {default}")
        setting = cls.query.filter_by(name=name).first()
        if setting:
            logger.info(f"Setting '{name}' found with value: {setting.value}")
            return setting.value
        logger.warning(f"Setting '{name}' not found. Returning default value: {default}")
        return default

    @classmethod
    def save(cls, name, value):
        """
        تنظیم یا به‌روزرسانی یک تنظیم خاص
        """
        redis_client = RedisClient()
        logger.info(f"Attempting to set setting '{name}'")
        setting = cls.query.filter_by(name=name).first()

        # رمزنگاری مقدار در صورت نیاز
        if name == 'smtp_password':
            if value == '******':
                logger.info("No changes detected in settings.")
                return setting
            encryption = Encryption()
            value = encryption.encrypt(value)
            logger.info(f"Password for setting '{name}' encrypted.")

        if setting:
            if setting.value != value:
                if name == 'smtp_password':
                    logger.info(f"Updating setting '{name}' from value: ****** to value: ******")
                else:
                    logger.info(f"Updating setting '{name}' from value: {setting.value} to value: {value}")
                setting.value = value
            else:
                logger.info("No changes detected in settings.")
                return setting

        else:
            logger.info(f"Creating new setting '{name}' with value: {value}")
            setting = cls(name=name, value=value)
            db.session.add(setting)

        db.session.commit()
        redis_client.set(setting.name, setting.value)
        logger.info(f"Setting '{name}' saved and cached successfully.")
        return setting

    @classmethod
    def save_bulk(cls, updates):
        """
        ذخیره یا به‌روزرسانی تنظیمات به‌صورت دسته‌ای
        """
        redis_client = RedisClient()
        logger.info(f"Bulk updating settings: {updates}")
        updated = False

        try:
            for name, value in updates.items():
                # رمزنگاری در صورت نیاز
                if name == 'smtp_password':
                    if value == '******':
                        logger.info("No changes detected in settings.")
                        continue
                    encryption = Encryption()
                    value = encryption.encrypt(value)
                    logger.info(f"Password for setting '{name}' encrypted.")

                setting = cls.query.filter_by(name=name).first()
                if setting:
                    if setting.value != value:
                        if name=='smtp_password':
                            logger.info(f"Updating setting '{name}' from value: ****** to value: ******")
                        else:
                            logger.info(f"Updating setting '{name}' from value: {setting.value} to value: {value}")
                        setting.value = value
                        updated = True
                else:
                    logger.info(f"Creating new setting '{name}' with value: {value}")
                    setting = cls(name=name, value=value)
                    db.session.add(setting)
                    updated = True

                redis_client.set(name, value)

            if updated:
                db.session.commit()
                logger.info("Settings saved successfully.")
            else:
                logger.info("No changes detected in settings.")

            return updated
        except Exception as e:
            logger.error(f"Error saving settings: {str(e)}")
            db.session.rollback()
            return False
