import bcrypt  # اضافه کردن ماژول bcrypt برای هش کردن رمز عبور
from flask_login import UserMixin
from .extensions import db

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    name = db.Column(db.String(150))
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False, default="customer")
    auth_provider = db.Column(db.String(50), default="local")

    def set_password(self, raw_password):
        # هش کردن رمز عبور
        self.password = bcrypt.hashpw(raw_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, raw_password):
        # بررسی رمز عبور
        return bcrypt.checkpw(raw_password.encode('utf-8'), self.password.encode('utf-8'))
