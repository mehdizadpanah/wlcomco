from flask import Flask
from .extensions import db, migrate, login_manager
from .routes import routes

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # تنظیمات از فایل config

    # مقداردهی اولیه اکستنشن‌ها
    db.init_app(app)
    migrate.init_app(app, db)  # راه‌اندازی Flask-Migrate
    login_manager.init_app(app)
    login_manager.login_view = 'routes.login'  # تنظیم مسیر لاگین پیش‌فرض

    # ثبت Blueprint
    app.register_blueprint(routes)

    return app
