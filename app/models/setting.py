from flask_login import UserMixin
from ..extensions import db,RedisClient,Encryption

class Setting(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=False)  # نوع Text برای ذخیره کد HTML

    def __repr__(self):
        return f"<Setting {self.name}: {self.value}>"

    @staticmethod
    def get_setting(name, default=None):
        setting = Setting.query.filter_by(name=name).first()
        if setting:
            return setting.value
        return default

    @staticmethod
    def set_setting(name, value):
        redis_client = RedisClient()
        setting = Setting.query.filter_by(name=name).first()

        if name == 'smtp_password':
            enctyption = Encryption()
            value = enctyption.encrypt (value)
    
        if setting:
            setting.value = value
        else:
            setting = Setting(name=name, value=value)
            db.session.add(setting)

        db.session.commit()
        redis_client.set(setting.name,setting.value)
        return setting
