from flask import Flask,g
from flask_login import current_user
from flask_migrate import upgrade
from sqlalchemy import inspect
from .extensions import db, migrate, login_manager, Utilities
from .routes import Blueprints
from .models import User,Setting,Notification
from .extensions import RedisClient


def create_app():
    migration = True
    app = Flask(__name__)
    app.config.from_object('config.Config')  # تنظیمات از فایل config


    # مقداردهی اولیه اکستنشن‌ها
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # تنظیم مسیر لاگین پیش‌فرض

    # ثبت Blueprint
    for bluprint in Blueprints:
        app.register_blueprint(bluprint)


    
    with app.app_context():
        migrate.init_app(app, db, directory="/var/www/wlcomco/migrations") # راه‌اندازی Flask-Migrate

        if migration==False:
            create_default_user()
            create_default_settings()
            create_default_notification_templates()
            load_settings_to_cache()
        else:
            try:
                # upgrade()  # اجرای میگریت برای به‌روزرسانی دیتابیس
                print("Database migrated successfully.")

            except Exception as e:
                 print(f"Migration failed: {e}")
                 raise

    @app.before_request
    def set_current_user():
        g.current_user = getattr(current_user, 'name', 'Anonymous')



    redisClient = RedisClient()
    app.config['APP_NAME'] = redisClient.get('app_title')
    @app.context_processor
    def inject_app_name():
        """اضافه کردن APP_NAME به تمام قالب‌ها"""
        return {'app_name': app.config.get('APP_NAME', redisClient.get('app_title')) or 'No Name'}


    return app

def create_default_notification_templates(): 
    """ایجاد رکوردهای پیش‌فرض برای قالب‌های ایمیل/پیامک"""
    default_templates = [
        {
            "name": "Email Verification",
            "send_via": "Email",
            "content_type": "HTML",
            "description": "This email template is used to send a verification link to users after they register or update their email address.",
            "subject": "Verify Your Email Address",
            "body": Utilities.load_email_body_from_file('templates/notification_templates/email_verification.html')
        },{
            "name": "Reset Password",
            "send_via": "Email",
            "content_type": "HTML",
            "description": "Thid email template is used to send a reset password link to user",
            "subject": "Reset your password",
            "body": Utilities.load_email_body_from_file('templates/notification_templates/reset_password.html')
        }]
    
    for template in default_templates:
        if not Notification.query.filter_by(name=template['name']).first():
            new_template = Notification(**template)
            db.session.add(new_template)
    
    db.session.commit()
    print("Default notification templates added.")

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
        "smtp_host": "smtp.example.com",
        "smtp_port": "587",
        "smtp_from": "admin@example.com",
        "smtp_username": "admin@example.com",
        "smtp_password": "password123",
        "smtp_security": "SSL",
        "registration_conf_email_temp": "<h1>Welcome to WLCOMCO!</h1>",  # نمونه قالب ایمیل,
        "app_title": "WLCOMCO",
        "logging_level":"WARNING",
        "logging_file_retention":"3",
        "logging_file_size":"10"
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
    redis_client = RedisClient()
    redis_client.flush()
    for s in Setting.query.all():
        redis_client.set(s.name,s.value)
    print("Settings loaded to cache.")


