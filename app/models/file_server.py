# file: app/models/file_server.py
import uuid
from sqlalchemy.dialects.mysql import BINARY
from ..extensions import db, get_logger, UnitUtils, Encryption, DBUtils
from .mixins import TimestampMixin, UserTrackingMixin

logger = get_logger('model')

class FileServer(db.Model, TimestampMixin, UserTrackingMixin):
    """
    جدول مربوط به سرورهای ذخیره‌سازی فایل
    """
    __tablename__ = 'file_server'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=DBUtils.generate_uuid)
    name = db.Column(db.String(100), nullable=False)
    host = db.Column(db.String(255), nullable=False)
    port = db.Column(db.Integer, nullable=True)
    storage_type = db.Column(db.Enum('LOCAL', 'FTP', 'SFTP', 'CLOUD', 'NFS'), nullable=False)
    path = db.Column(db.String(1024), nullable=False)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    api_key = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)

    def __repr__(self):
        return f"<FileServer name={self.name}, host={self.host}, type={self.storage_type}>"

    @classmethod
    def get_all(cls):
        """
        دریافت لیست تمامی سرورهای فایل ذخیره‌شده.
        """
        logger.info("Fetching all file servers from the database.")
        return cls.query.all()

    @classmethod
    def get_by_id(cls, server_id):
        """
        دریافت سرور فایل بر اساس شناسه (UUID).
        """
        logger.info(f"Fetching file server by ID: {server_id}")
        try:
            binary_id = UnitUtils.hex_to_bytes(server_id)
            return cls.query.get(binary_id)
        except Exception as e:
            logger.error(f"Failed to get file server with id {server_id}: {str(e)}")
            return None

    def save(self):
        """
        ذخیره یا بروزرسانی رکورد فعلی در دیتابیس
        """
        logger.info(f"Saving file server: {self.name} ({self.host})")

        try:
            if not db.session.object_session(self):

                self.id = DBUtils.generate_uuid()
                if self.password:
                    self.password = Encryption.encrypt(self.password)
                db.session.add(self)
            else:
                if self.password and self.password != "******":
                    logger.info("Encrypting new password before saving.")
                    self.password = Encryption.encrypt(self.password)

            db.session.commit()
            logger.info("File server saved successfully.")
            return True

        except Exception as e:
            logger.error(f"Error saving file server: {str(e)}")
            db.session.rollback()
            return False

    def delete(self):
        """
        حذف سرور فایل از دیتابیس
        """
        logger.info(f"Deleting file server: {self.name}")
        try:
            db.session.delete(self)
            db.session.commit()
            logger.info("File server deleted successfully.")
            return True
        except Exception as e:
            logger.error(f"Error deleting file server: {str(e)}")
            db.session.rollback()
            return False

    def get_id_hex(self):
        """بازگرداندن شناسه باینری (UUID) به صورت رشته هگز."""
        return UnitUtils.bytes_to_hex(self.id)

