from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

db = SQLAlchemy()
login_manager = LoginManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'login'

    from .routes import routes  # ایمپورت Blueprint از routes.py
    app.register_blueprint(routes)  # ثبت Blueprint در اپلیکیشن

    with app.app_context():
        from . import routes, models
        db.create_all()

    return app