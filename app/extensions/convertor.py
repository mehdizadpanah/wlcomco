from sqlalchemy.inspection import inspect
from datetime import datetime
import logging
import binascii
import ast



logger = logging.getLogger('extentions')

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
            # اگر ورودی از قبل یک رشته هگز است، بدون تغییر برگردان
            if isinstance(bin_bytes, str):
                logger.info("Input is already a hex string.")
                return bin_bytes
            
            # در صورتیکه ورودی از نوع memoryview یا bytearray باشد، ابتدا به bytes تبدیل کن
            if isinstance(bin_bytes, (memoryview, bytearray)):
                logger.info("Converting input to bytes.")
                bin_bytes = bytes(bin_bytes)
            
            # تبدیل bytes به رشته هگز
            return binascii.hexlify(bin_bytes).decode('utf-8')
        
        except Exception as e:
            # ثبت خطا با پیام صحیح که به عملکرد تابع اشاره دارد
            logger.critical(f"Error occurred while converting bytes to hex: {str(e)}")
            raise

    @staticmethod
    def hex_to_bytes(hex_str):
        try:
            # ثبت مقدار دریافتی و نوع آن در لاگ
            logger.info(f"Received value in hex_to_bytes: {hex_str}, Type: {type(hex_str)}")

            # اگر مقدار از نوع `memoryview` یا `bytearray` بود، به `bytes` تبدیل کن
            if isinstance(hex_str, (memoryview, bytearray)):
                logger.info("Converting memoryview or bytearray to bytes.")
                hex_str = bytes(hex_str)

            # اگر ورودی از نوع str باشد ولی به نظر برسد که نمایش داده شده یک شیء bytes است،
            # تلاش می‌کنیم آن را به bytes تبدیل کنیم
            if isinstance(hex_str, str):
                logger.info("Trying to convert string to bytes.")
                stripped = hex_str.strip()
                if (stripped.startswith("b'") and stripped.endswith("'")) or \
                (stripped.startswith('b"') and stripped.endswith('"')):
                    try:
                        hex_str = ast.literal_eval(stripped)
                        logger.info("Converted string representation of bytes to bytes object.")
                    except Exception as eval_err:
                        logger.error(f"Failed to evaluate bytes literal: {eval_err}")
                        # در صورت شکست، همچنان ادامه می‌دهیم تا خطا در unhexlify ایجاد شود.

            # اگر مقدار از قبل `bytes` است و طول آن 16 بایت است، از تبدیل صرف نظر کن
            if isinstance(hex_str, bytes) and len(hex_str) == 16:
                logger.info("Input is already a valid 16-byte binary.")
                return hex_str  # مقدار باینری معتبر است، بدون تغییر برگردانده شود

            # اگر مقدار `str` است، تبدیل به بایت انجام شود
            if isinstance(hex_str, str):
                logger.info("Converting string to bytes.")
                return binascii.unhexlify(hex_str)

            # اگر نوع ورودی نامعتبر باشد، خطا ایجاد کن
            raise ValueError("Invalid input type for hex_to_bytes.")

        except Exception as e:
            logger.critical(f"Error occurred while converting hex to byte: {str(e)}")
            raise e

