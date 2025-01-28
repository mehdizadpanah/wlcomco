import os
from ..extensions import get_logger

logger = get_logger('extentions')

class Utilities:
    @staticmethod
    def load_email_body_from_file(template_path):
        """
        این تابع متن فایل HTML را می‌خواند و به عنوان رشته برمی‌گرداند.
        :param template_path: مسیر فایل HTML
        :return: متن فایل به صورت رشته
        """
        logger.info(f"Attempting to load email body from file: {template_path}")

        # بررسی وجود فایل
        if not os.path.exists(template_path):
            logger.error(f"Template file not found: {template_path}")
            raise FileNotFoundError(f"Template file not found: {template_path}")

        try:
            # خواندن محتوای فایل
            with open(template_path, 'r', encoding='utf-8') as file:
                content = file.read()
                logger.info(f"Email template loaded successfully from: {template_path}")
                return content
        except Exception as e:
            # ثبت خطای غیرمنتظره
            logger.critical(f"Error occurred while loading email template from {template_path}: {str(e)}")
            raise
