import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from .encryption import Encryption
from .redis_client import RedisClient
from flask import flash
from ..extensions.logging_client import get_logger

logger = get_logger("extentions")

class EmailSender:
    def __init__(self):
        """
        مقداردهی اولیه و اتصال به Redis برای دریافت تنظیمات.
        """
        redis_client = RedisClient()


        self.smtp_host = str(redis_client.get("smtp_host"))
        self.smtp_port = int(redis_client.get("smtp_port"))
        self.smtp_username = redis_client.get("smtp_username")
        self.smtp_password = Encryption.decrypt(redis_client.get("smtp_password"))
        self.smtp_from = redis_client.get("smtp_from")
        self.smtp_security = redis_client.get("smtp_security").upper()

    def send_email(self, subject, recipients, body, html=None):
        """
        ارسال ایمیل با استفاده از تنظیمات دینامیک.
        """
        try:
            # پیکربندی پیام ایمیل
            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = self.smtp_from
            msg["To"] = ", ".join(recipients)

            # اضافه کردن متن ساده و HTML
            msg.attach(MIMEText(body, "plain"))
            if html:
                msg.attach(MIMEText(html, "html"))

            # انتخاب نوع امنیت SMTP
            if self.smtp_security == "SSL":
                server = smtplib.SMTP_SSL(self.smtp_host, self.smtp_port)
            else:  # TLS یا حالت بدون امنیت
                server = smtplib.SMTP(self.smtp_host, self.smtp_port)
                if self.smtp_security == "TLS":
                    server.starttls()

            # ورود به SMTP
            if self.smtp_username and self.smtp_password:
                server.login(self.smtp_username, self.smtp_password)
                logger.info("Login to SMTP server successful.")


            # ارسال ایمیل
            server.sendmail(self.smtp_from, recipients, msg.as_string())
            logger.info("Email sent successfully.")
            server.quit()

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            raise e






