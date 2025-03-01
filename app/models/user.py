import bcrypt 
from flask_login import UserMixin
from ..extensions import db,get_logger,UnitUtils
from itsdangerous import URLSafeTimedSerializer
from flask import current_app
import uuid
from sqlalchemy.dialects.mysql import BINARY




def generate_uuid():
    """
    تولید یک مقدار باینری 16 بایتی (UUID نسخه 4).
    """
    return uuid.uuid4().bytes  # bytes شکل باینری UUID


logger = get_logger('model')

class User(UserMixin, db.Model):
    __tablename__ = 'user'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_general_ci'}

    id = db.Column(BINARY(16), primary_key=True, default=generate_uuid)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150))
    password = db.Column(db.String(200))
    role = db.Column(db.String(50), nullable=False, default="customer")
    auth_provider = db.Column(db.String(50), nullable=False, default="local")
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), nullable=True)
    password_reset_token = db.Column(db.String(255), nullable=True)
        # فیلد جدید برای تعیین زبان کاربر
    language_id = db.Column(BINARY(16), db.ForeignKey('language.id'), nullable=True)

    # تعریف رابطه برای دسترسی راحت‌تر به اطلاعات زبان
    language = db.relationship('Language', backref='user', lazy=True)


    def get_id(self):
        try:
            return UnitUtils.bytes_to_hex(self.id)
        except AttributeError:
            raise NotImplementedError("No `id` attribute - override `get_id`") from None

    def save_fields(self, updates):
        """
        ذخیره یا به‌روزرسانی فیلدهای مشخص‌شده برای کاربر.

        :param updates: دیکشنری شامل فیلدها و مقادیر جدید آن‌ها
        :return: True اگر تغییری ایجاد یا ذخیره شد، False اگر هیچ تغییری ایجاد نشد.
        """
        logger.info(f"Attempting to save/update fields for user: {self.email}")
        updated = False
        if not updates:
            logger.info("No updates provided for user.")
            return False

        try:
            for field, new_value in updates.items():
                if hasattr(self, field):
                    current_value = getattr(self, field)

                    if field == "password":
                        if not self.check_password(new_value):  # بررسی تغییر رمز عبور
                            self.set_password(new_value)  # هش کردن رمز عبور
                            logger.info(f"Password updated for user: {self.email}")
                            updated = True
                    elif current_value != new_value:  # بررسی تغییر سایر فیلدها
                        logger.info(
                            f"Field '{field}' changed for user {self.email}: "
                            f"from '{current_value}' to '{new_value}'"
                        )
                        setattr(self, field, new_value)
                        updated = True

            if updated:
                db.session.add(self)  # اضافه کردن کاربر به جلسه
                db.session.commit()  # ذخیره تغییرات
                logger.info(f"Changes saved for user: {self.email}")
                return True
            else:
                logger.info(f"No changes detected for user: {self.email}")
                return False

        except Exception as e:
            logger.error(f"Error saving user fields for {self.email}: {str(e)}")
            return False

    def set_password(self, raw_password):
        """
        Sets a hashed password for the user.

        :param raw_password: The raw password to hash and store.
        """
        try:
            # هش کردن رمز عبور
            self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            logger.info(f"Password set successfully for user: {getattr(self, 'email', 'Unknown User')}")
        except Exception as e:
            logger.critical(f"Failed to set password for user: {getattr(self, 'email', 'Unknown User')}. Error: {str(e)}")
            raise

    def check_password(self, raw_password):
        """
        بررسی رمز عبور ورودی با رمز عبور هش شده ذخیره‌شده.

        :param raw_password: رمز عبور وارد شده توسط کاربر.
        :return: True اگر رمز عبور مطابقت داشته باشد، False در غیر این صورت.
        """
        if not raw_password:
            logger.warning("Empty password provided for user check.")
            return False

        try:
            if self.password:
                is_valid = bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))
                if is_valid:
                    logger.info(f"Password check passed for user: {self.email}")
                else:
                    logger.warning(f"Password check failed for user: {self.email}")
                return is_valid

            logger.error(f"No password set for user: {self.email}")
            return False

        except Exception as e:
            logger.critical(f"Error while checking password for user {self.email}: {str(e)}")
            return False
    
    def set_token(self,salt):
        """
        ایجاد توکن تایید ایمیل و ذخیره آن در مدل کاربر.

        :return: None
        """
        try:
            if not self.email:
                logger.error("Cannot generate verification token: Email is not set.")
                return

            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            if salt == 'password-reset':
                self.password_reset_token = serializer.dumps(self.email,salt=salt)
                logger.info(f"Password verification token generated for user: {self.email}")
            elif salt == 'email-confirm':
                self.email_verification_token = serializer.dumps(self.email, salt=salt)
                logger.info(f"Email verification token generated for user: {self.email}")
            else: 
                logger.info(f"Salt is wrong for user: {self.email}")


        except Exception as e:
            logger.critical(f"Error generating email verification token for user {self.email}: {str(e)}")

    def verify_token(self, token, salt, expiration=7200):
        """
        بررسی و تایید صحت توکن ایمیل

        :param token: توکن ایمیل برای تایید
        :param expiration: مدت زمان انقضا به ثانیه (پیش‌فرض: 7200)
        :return: True اگر توکن معتبر باشد، False در غیر این صورت
        """
        if not token:
            logger.warning("Empty token provided for user lookup.")
            return None
        
        try:
            serializer = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
            email = serializer.loads(token, salt=salt, max_age=expiration)
            if email.strip().lower() == self.email.strip().lower():
                logger.info(f"Token verified successfully for user: {self.email}")
                return True
            else:
                logger.warning(f"Email token verification failed: Token email does not match user email ({self.email}).")
                return False

        except ValueError as ve:
            logger.warning(f"Invalid token format for user {self.email}: {str(ve)}")
            return False
        except Exception as e:
            logger.error(f"Error verifying email token for user {self.email}: {str(e)}")
            return False

    @classmethod
    def get_by_email(cls, email):
        """
        جستجوی کاربر با استفاده از ایمیل.

        :param email: ایمیل کاربر مورد نظر.
        :return: شیء کاربر در صورت یافتن، در غیر این صورت None.
        """
        logger.info(f"Attempting to find user with email: {email}")
        if not email:
            logger.warning("Empty email provided for user lookup.")
            return None

        try:

            user = cls.query.filter_by(email=email).first()
            if user:
                logger.info(f"User found with email: {email}")
            else:
                logger.warning(f"No user found with email: {email}")
            return user

        except Exception as e:
            logger.error(f"Error occurred while finding user with email {email}: {str(e)}")
            return None

    @classmethod
    def get_by_token(cls, token, token_type):
        """
        جستجوی کاربر بر اساس توکن تایید ایمیل یا توکن بازنشانی رمز عبور.

        :param token: توکن مورد جستجو.
        :param token_type: نوع توکن ("email_verification" یا "password_reset").
        :return: شیء کاربر در صورت یافتن، در غیر این صورت None.
        """
        if not token:
            logger.warning("Empty token provided for user lookup.")
            return None
        if not token_type:
            logger.warning("Empty token_type provided for user lookup.")
            return None

        try:
            if token_type == "email_verification_token":
                logger.info(f"Searching for user with email verification token: {token}")
                user = cls.query.filter_by(email_verification_token=token).first()
            elif token_type == "password_reset_token":
                logger.info(f"Searching for user with password reset token: {token}")
                user = cls.query.filter_by(password_reset_token=token).first()
            else:
                logger.warning(f"Invalid token type provided: {token_type}")
                return None

            if user:
                logger.info(f"User found with {token_type} token: {user.email}")
            else:
                logger.warning(f"No user found with {token_type} token: {token}")
            return user

        except Exception as e:
            logger.error(f"Error occurred while searching for user with {token_type} token: {str(e)}")
            return None
