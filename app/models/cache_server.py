# file: app/models/cache_server.py
import uuid
from sqlalchemy.dialects.mysql import BINARY
from ..extensions import db, get_logger, UnitUtils,Encryption,DBUtils
from .mixins import TimestampMixin, UserTrackingMixin

logger = get_logger('model')

class CacheServer(db.Model, TimestampMixin, UserTrackingMixin):
    """
    جدول مخصوص ذخیره اطلاعات سرورهای کش
    """
    __tablename__ = 'cache_server'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=DBUtils.generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=False, default=6379)
    password = db.Column(db.String(255), nullable=True)
    db_index = db.Column(db.Integer, nullable=False, default=0)
    description = db.Column(db.Text, nullable=True)
    
    def __repr__(self):
        return f"<CacheServer name={self.name}, host={self.host}, port={self.port}, db_index={self.db_index}>"

   
    @classmethod
    def get_all(cls):
        """
        بازگرداندن لیست تمام سرورهای کش ذخیره‌شده.
        """
        logger.info("Fetching all cache servers from the database.")
        return cls.query.all()

    @classmethod
    def get_by_id(cls, server_id):
        """
        دریافت سرور کش بر اساس شناسه (UUID).
        ورودی server_id باید رشته هگز باشد (مثال: 'A1B2C3...') که به باینری تبدیل می‌کنیم.
        در صورت موفقیت رکورد برمی‌گردد، در غیر این صورت None.
        """
        logger.info(f"Fetching cache server by ID: {server_id}")
        if not server_id:
            logger.warning("Empty server_id provided.")
            return None

        try:
            binary_id = UnitUtils.hex_to_bytes(server_id)
            return cls.query.get(binary_id)
        except Exception as e:
            logger.error(f"Failed to get cache server with id {server_id}: {str(e)}")
            return None

    def save(self):
        """
        ذخیره یا بروزرسانی رکورد فعلی در دیتابیس
        """
        logger.info(f"Saving cache server: {self.name} ({self.host}:{self.port}/{self.db_index})")
        
        # استفاده از نمونه‌ای از کلاس رمزنگاری (Encryption)
        try:
            new = db.session.object_session(self) is None  # تعیین می‌کنیم که آیا رکورد جدید است یا خیر

            if new:
                # مقداردهی ID برای رکورد جدید
                self.id = DBUtils.generate_uuid()  # تابع تولید UUID

                # رمزنگاری پسورد
                if self.password:
                    logger.info("Encrypting password before saving.")
                    self.password = Encryption.encrypt(self.password)
                db.session.add(self)  # اضافه کردن به سشن برای ایجاد رکورد جدید

            else:
                self.id = UnitUtils.hex_to_bytes(self.id)
                # بررسی مقدار پسورد در حالت ویرایش
                if self.password and self.password != "******":
                    logger.info("Encrypting new password before saving.")
                    self.password = Encryption.encrypt(self.password)
                else:
                    # مقدار قبلی را از دیتابیس بخوانید و نگه دارید
                    with db.session.no_autoflush:
                        existing_password = db.session.execute(
                            db.select(CacheServer.password).where(CacheServer.id == self.id)
                        ).scalar()

                    if existing_password:
                        self.password = existing_password  # حفظ مقدار قبلی

            db.session.commit()
            logger.info("Cache server saved successfully.")
            return True

        except Exception as e:
            logger.error(f"Error saving cache server: {str(e)}")
            db.session.rollback()
            return False

    def delete(self):
        """
        حذف رکورد فعلی از دیتابیس
        """
        logger.info(f"Deleting cache server: {self.name}")
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info("Cache server deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"Error deleting cache server: {str(e)}")
            db.session.rollback()
            return False

    def get_id_hex(self):
        """بازگرداندن شناسه باینری (UUID) به صورت رشته هگز."""
        return UnitUtils.bytes_to_hex(self.id)
