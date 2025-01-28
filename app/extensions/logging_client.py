import logging
from logging.handlers import RotatingFileHandler
from . import RedisClient
from flask import g


def get_logger(name):
    logger = logging.getLogger(name)
    redisClient = RedisClient()
    if not logger.handlers:  # جلوگیری از اضافه کردن چند هندلر تکراری
        # خواندن تنظیمات از دیتابیس یا کش
        log_file_retention = int(redisClient.get('logging_file_retention') or 3)  # تعداد نسخه‌های لاگ
        log_level = redisClient.get('logging_level').upper() or "WARNING" # سطح لاگ
        log_file_size = int(redisClient.get('logging_file_retention') or 10)  # حجم فایل لاگ

        # هندلر برای فایل با چرخش لاگ
        file_handler = RotatingFileHandler(
            f'/var/log/wlcomco/{name}.log',
            maxBytes=log_file_size * 1024 * 1024,  # حداکثر حجم فایل (5 مگابایت)
            backupCount=log_file_retention  # تعداد فایل‌های نگهداری
        )
        file_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [User: %(user)s] - %(message)s'))
        logger.addHandler(file_handler)

        # هندلر برای کنسول
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - [User: %(user)s] - %(message)s'))
        logger.addHandler(console_handler)

        # تنظیم سطح لاگ
        logger.setLevel(getattr(logging, log_level, logging.INFO))
        logger.addFilter(UserFilter())

    return logger
# اضافه کردن نام کاربر جاری به رکوردهای لاگ
class UserFilter(logging.Filter):
    def filter(self, record):
        record.user = getattr(g, 'current_user', 'Anonymous')  # اگر کاربر وجود نداشت، Anonymous
        return True

# اضافه کردن فیلتر به لاگر
logger = get_logger('app')
logger.addFilter(UserFilter())
