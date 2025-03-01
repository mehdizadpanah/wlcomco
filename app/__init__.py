from flask import Flask, g
from flask_login import current_user
from flask_migrate import upgrade
from .extensions import db, migrate, login_manager, Utilities
from .routes import Blueprints
from .models import User, Setting, Notification, Language
from .extensions import RedisClient
from .services import get_translation,get_active_language,gettext


def create_app():
    migration = False
    app = Flask(__name__)
    app.config.from_object('config.Config')  # تنظیمات از فایل config

    # مقداردهی اولیه اکستنشن‌ها
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'  # تنظیم مسیر لاگین پیش‌فرض

    # ثبت Blueprint
    for blueprint in Blueprints:
        app.register_blueprint(blueprint)

    with app.app_context():
        migrate.init_app(app, db, directory="/var/www/wlcomco/migrations")  # راه‌اندازی Flask-Migrate

        if not migration:
            create_default_user()
            create_default_settings()
            create_default_notification_templates()
            load_settings_to_cache()
            create_default_language()
        else:
            try:
                upgrade()  # اجرای میگریت برای به‌روزرسانی دیتابیس
                print("Database migrated successfully.")
            except Exception as e:
                print(f"Migration failed: {e}")
                raise

    @app.before_request
    def set_current_user_and_language():
        g.current_user = getattr(current_user, 'name', 'Anonymous')  # تنظیم نام کاربر

        # تنظیم زبان فعال
        default_language = Language.query.filter_by(default=True).first()

        if current_user.is_authenticated and current_user.language_id:
            user_language = Language.query.filter_by(id=current_user.language_id, is_active=True).first()
            if user_language:
                g.current_language = user_language.code
            else:
                g.current_language = default_language.code
        else:
            g.current_language = default_language.code

    redis_client = RedisClient()
    app.config['APP_NAME'] = redis_client.get('app_title')

    @app.context_processor
    def inject_globals():
        active_language_id,is_rtl = get_active_language()
        # اگر زبان فعال و فیلد rtl آن True باشد، مقدار rtl و در غیر این صورت ltr برگردانده می‌شود.
        direction = "rtl" if is_rtl else "ltr"

        return {
            'app_name': app.config.get('APP_NAME', redis_client.get('app_title')) or 'No Name',
            # 'active_language': get_active_language(),
            'gettext': gettext,
            'get_translation': get_translation,
            'direction': direction

        }

    return app



# ======= ایجاد داده‌های پیش‌فرض =======


def create_default_notification_templates():
    """ایجاد رکوردهای پیش‌فرض برای قالب‌های ایمیل/پیامک"""
    default_templates = [
        {
            "name": "Email Verification",
            "send_via": "Email",
            "content_type": "HTML",
            "description": "Verification email template.",
            "subject": "Verify Your Email Address",
            "body": Utilities.load_email_body_from_file('templates/notification_templates/email_verification.html')
        },
        {
            "name": "Reset Password",
            "send_via": "Email",
            "content_type": "HTML",
            "description": "Password reset template.",
            "subject": "Reset your password",
            "body": Utilities.load_email_body_from_file('templates/notification_templates/reset_password.html')
        }
    ]
    
    for template in default_templates:
        if not Notification.query.filter_by(name=template['name']).first():
            new_template = Notification(**template)
            db.session.add(new_template)

    db.session.commit()
    print("Default notification templates added.")

def create_default_user():
    """ایجاد کاربر پیش‌فرض اگر وجود نداشته باشد"""
    email = "meh.izadpanah@gmail.com"
    user = User.query.filter_by(email=email).first()

    if not user:
        new_user = User(
            email=email,
            name="Mehdi Izadpanah",
            role="admin",
            auth_provider="google"
        )
        db.session.add(new_user)
        db.session.commit()
        print(f"Default user with email {email} created.")

def create_default_settings():
    """کنترل و ساخت تنظیمات پیش‌فرض"""
    default_settings = {
        "smtp_host": "smtp.example.com",
        "smtp_port": "587",
        "smtp_from": "admin@example.com",
        "smtp_username": "admin@example.com",
        "smtp_password": "password123",
        "smtp_security": "SSL",
        "registration_conf_email_temp": "<h1>Welcome to WLCOMCO!</h1>",
        "app_title": "WLCOMCO",
        "logging_level": "WARNING",
        "logging_file_retention": "3",
        "logging_file_size": "10"
    }

    existing_settings = Setting.query.with_entities(Setting.name).all()
    existing_names = {s.name for s in existing_settings}

    new_settings = [
        Setting(name=name, value=value)
        for name, value in default_settings.items() if name not in existing_names
    ]

    if new_settings:
        db.session.bulk_save_objects(new_settings)
        db.session.commit()
        print(f"{len(new_settings)} new settings added.")
    else:
        print("All default settings already exist.")

def load_settings_to_cache():
    """ارسال تنظیمات به کش"""
    redis_client = RedisClient()
    redis_client.flush()
    for s in Setting.query.all():
        redis_client.set(s.name, s.value)
    print("Settings loaded to cache.")

def create_default_language():
    """افزودن زبان پیش‌فرض در صورت عدم وجود"""
    if not Language.get_by_code('en'):
        english = Language(code='en', name='English', is_active=True, default=True)
        english.save()
        print("Default language (English) added.")
    else:
        print("Default language already exists.")
