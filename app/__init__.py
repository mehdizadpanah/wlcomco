from flask import Flask
from .extensions import db, migrate, login_manager
from .routes import Blueprints
from .models import User  


def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')  # تنظیمات از فایل config

    # مقداردهی اولیه اکستنشن‌ها
    db.init_app(app)
    migrate.init_app(app, db)  # راه‌اندازی Flask-Migrate
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # تنظیم مسیر لاگین پیش‌فرض

    # ثبت Blueprint
    for bluprint in Blueprints:
        app.register_blueprint(bluprint)

    with app.app_context():
        create_default_user()

    return app


def create_default_user():
    """ایجاد کاربر پیش‌فرض اگر وجود نداشته باشد"""
    email = "meh.izadpanah@gmail.com"
    user = User.query.filter_by(email=email).first()

    if not user:
        new_user = User(
            email=email,
            name="Mehdi Izadpanah",
            role="admin",  # سطح دسترسی سرویس‌دهنده
            auth_provider="google"  # مشخص کردن نوع کاربر به عنوان گوگل
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"Default user with email {email} created.")