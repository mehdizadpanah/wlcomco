from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager
import uuid


db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()

class DBUtils:
    @staticmethod
    def generate_uuid():
        """تولید یک مقدار باینری 16 بایتی (UUID نسخه 4)"""
        return uuid.uuid4().bytes






