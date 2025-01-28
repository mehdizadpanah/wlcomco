import uuid
from ..extensions import db,get_logger,RedisClient,ModelUtils
from .mixins import TimestampMixin, UserTrackingMixin
from sqlalchemy.dialects.mysql import BINARY




def generate_uuid():
    """
    تولید یک مقدار باینری 16 بایتی (UUID نسخه 4).
    """
    return uuid.uuid4().bytes  # bytes شکل باینری UUID


logger = get_logger('model')
redis_client = RedisClient()

class Notification(db.Model, TimestampMixin, UserTrackingMixin):
    __tablename__ = 'notification_template'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=generate_uuid)
    name = db.Column(db.String(255), unique=True, nullable=False)
    send_via = db.Column(db.Enum('email', 'sms', collation='utf8mb4_general_ci'), nullable=False)
    content_type = db.Column(db.Enum('text', 'html'), nullable=False)
    description = db.Column(db.Text, nullable=True)
    subject = db.Column(db.String(255), nullable=True)
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Notification {self.name}>"


    @classmethod
    def get_by_name(cls, notification_name):
        """
        جستجوی نوتیفیکیشن بر اساس نام و ذخیره در کش.
        """
        logger.info(f"Fetching notification with name: {notification_name}")

        try:
            # جستجو در پایگاه داده
            notification = cls.query.filter_by(name=notification_name).first()
            if notification:
                logger.info(f"Notification {notification_name} found in database. Caching it.")

                # redis_client.set(f"notification:name:{notification_name}",json.dumps(ModelUtils.to_dict(notification)),ex=3600)
                return notification
            else:
                logger.warning(f"Notification {notification_name} not found in database.")
                return None

        except Exception as e:
            logger.error(f"Error fetching notification {notification_name}: {str(e)}")
            return None

    def save(self,original_data=None):
        """
        ذخیره یا به‌روزرسانی یک نوتیفیکیشن و بررسی تغییرات با استفاده از کش.
        """
        logger.info(f"Saving notification: {self.name}")

        try:
            if original_data:
                # بررسی تغییرات
                for field, new_value in ModelUtils.to_dict(self).items():
                    old_value = original_data.get(field)
                    if old_value != new_value:
                        logger.info(
                            f"Field '{field}' changed for notification '{self.name}': "
                            f"from '{old_value}' to '{new_value}'"
                        )

            # ذخیره در پایگاه داده
            if db.session.object_session(self) is None:
                # اتصال یا merge کردن شیء به session
                self = db.session.merge(self)
                logger.info(f"Notification {self.name} merged into session.")

            db.session.commit()
            logger.info(f"Notification saved successfully: {self.name}")
            return True

        except Exception as e:
            logger.error(f"Error saving notification {self.name}: {str(e)}")
            db.session.rollback()
            return False

    @classmethod
    def get_all(cls):
        """
        دریافت تمام نوتیفیکیشن‌ها.
        """
        logger.info("Fetching all notifications.")
        try:
            notifications = cls.query.all()
            if notifications:
                logger.info(f"Total notifications fetched: {len(notifications)}")
            else:
                logger.warning("No notifications found in the database.")
            return notifications
        except Exception as e:
            logger.error(f"Error occurred while fetching all notifications: {str(e)}")
            return []
