from flask import Flask
from .extensions import db, migrate, login_manager
from .routes import Blueprints
from .models import User,Setting
from .extensions import RedisClient


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
        create_default_settings()
        load_settings_to_cache()

    return app


def create_default_user(): # ساخت کاربر پیش فرض
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

def create_default_settings(): # کنترل و ساخت تنظیمات دیفات
    default_settings = {
        "app_name": "WLCOMCO",
        "smtp_host": "smtp.example.com",
        "smtp_port": "587",
        "smtp_username": "admin@example.com",
        "smtp_password": "password123",
        "smtp_security": "SSL",
        "registration_conf_email_temp": "<h1>Welcome to WLCOMCO!</h1>"  # نمونه قالب ایمیل
    }

    # خواندن همه تنظیمات موجود
    existing_settings = Setting.query.with_entities(Setting.name).all()
    existing_names = {s.name for s in existing_settings}

    new_settings = []
    for name, value in default_settings.items():
        if name not in existing_names:
            new_settings.append(Setting(name=name, value=value))

    # اضافه کردن و ذخیره فقط تنظیمات جدید
    if new_settings:
        db.session.bulk_save_objects(new_settings)
        db.session.commit()
        print(f"{len(new_settings)} new settings added.")
    else:
        print("All default settings already exist.")

def load_settings_to_cache(): #ارسال همه تنظیمات به کش
    resius_client = RedisClient()
    resius_client.flush()
    for s in Setting.query.all():
        resius_client.set(s.name,s.value)
    print("Settings loaded to cache.")


