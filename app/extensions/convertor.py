from sqlalchemy.inspection import inspect
from datetime import datetime
import logging
import binascii


logger = logging.getLogger('model_utils')

class ModelUtils:
    @staticmethod
    def to_dict(instance):
        """
        تبدیل یک آبجکت مدل SQLAlchemy به دیکشنری.

        :param instance: شیء مدل SQLAlchemy.
        :return: دیکشنری شامل داده‌های مدل.
        """
        try:
            logger.info(f"Converting {instance.__class__.__name__} instance to dictionary.")
            mapper = inspect(instance.__class__)
            columns = [column.key for column in mapper.columns]

            data = {}
            for column in columns:
                value = getattr(instance, column)

                # تبدیل datetime به ISO format
                if isinstance(value, datetime):
                    data[column] = value.isoformat()
                else:
                    data[column] = value

            return data

        except Exception as e:
            logger.error(f"Error converting model to dictionary: {str(e)}")
            return {}

    @staticmethod
    def from_dict(cls, data):
        """
        تبدیل دیکشنری به آبجکت مدل SQLAlchemy.

        :param cls: کلاس مدل SQLAlchemy.
        :param data: دیکشنری شامل داده‌ها.
        :return: آبجکت مدل با داده‌های مقداردهی‌شده.
        """
        try:
            logger.info(f"Converting dictionary to {cls.__name__} instance.")
            mapper = inspect(cls)
            columns = [column.key for column in mapper.columns]

            instance_data = {}
            for column in columns:
                if column in data:
                    column_type = getattr(cls, column).type

                    # تبدیل رشته به datetime در صورت نیاز
                    if isinstance(column_type, db.DateTime) and data[column] is not None:
                        instance_data[column] = datetime.fromisoformat(data[column])
                    else:
                        instance_data[column] = data[column]

            return cls(**instance_data)

        except Exception as e:
            logger.error(f"Error converting dictionary to {cls.__name__}: {str(e)}")
            return None

class UnitUtils:
    @staticmethod
    def bytes_to_hex(bin_bytes):
        try:
            return binascii.hexlify(bin_bytes).decode('utf-8')
        except Exception as e:
            # ثبت خطای غیرمنتظره
            logger.critical(f"Error occurred while converting hex to byte: {str(e)}")
            raise

    
    @staticmethod
    def hex_to_bytes(hex_str):
        try:
            return binascii.unhexlify(hex_str)
        except Exception as e:
            # ثبت خطای غیرمنتظره
            logger.critical(f"Error occurred while converting hex to byte : {str(e)}")
            raise

