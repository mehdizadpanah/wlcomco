import bcrypt 
from flask_login import UserMixin
from ..extensions import db
from itsdangerous import URLSafeTimedSerializer
from flask import current_app


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150))
    password = db.Column(db.String(200))
    role = db.Column(db.String(50), nullable=False, default="customer")
    auth_provider = db.Column(db.String(50), nullable=False, default="local")
    is_email_verified = db.Column(db.Boolean, default=False)
    email_verification_token = db.Column(db.String(255), nullable=True)
    password_reset_token = db.Column(db.String(255), nullable=True)


    def set_password(self, raw_password):
        # هش کردن رمز عبور
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, raw_password):
        # بررسی رمز عبور
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))
    
    def set_email_verification_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        self.email_verification_token = s.dumps(self.email, salt='email-confirm')

    def verify_email_token(self, token, expiration=7200):
        """
        بررسی توکن ایمیل و تأیید صحت آن
        :param token: توکن ایمیل
        :param expiration: زمان انقضا به ثانیه
        :return: True اگر توکن معتبر باشد، در غیر این صورت False
        """
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='email-confirm', max_age=expiration)
        except Exception as e:
            # برای دیباگ می‌توانید نوع خطا را چاپ کنید
            print(f"Token verification error: {e}")
            return False

        # بررسی صحت ایمیل
        return email.strip().lower() == self.email.strip().lower()

    def set_password_reset_token(self):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        self.password_reset_token = s.dumps(self.email, salt='password-reset')

    def verify_password_reset_token(self, token, expiration=7200):
        s = URLSafeTimedSerializer(current_app.config['SECRET_KEY'])
        try:
            email = s.loads(token, salt='password-reset', max_age=expiration)
        except:
            return False
        return email == self.email

