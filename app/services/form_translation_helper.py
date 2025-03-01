from flask_login import current_user
from flask import after_this_request
from ..models import Translation, TranslationValue,Language
from ..extensions import get_logger,UnitUtils
from flask import request,make_response




logger = get_logger('services')

def get_active_language():
    """
    برگرداندن زبان منتخب
    """
    try:
        if current_user.is_authenticated:
            cookie_language_name = f"user_lang_{current_user.email}"
            cookie_rtl_name = f"user_rtl_{current_user.email}"

            cookie_lan_id_hex = request.cookies.get(cookie_language_name)
            if cookie_lan_id_hex:
                # کوکی موجود => تبدیل هگز به بایت
                lang_id_bytes = UnitUtils.hex_to_bytes(cookie_lan_id_hex)
                logger.info("Active language retrieved from cookie (bytes): %s", lang_id_bytes)

            cookie_rtl_val = request.cookies.get(cookie_rtl_name)
            if cookie_rtl_val:
                # کوکی موجود => تبدیل به بولین
                is_rtl = (cookie_rtl_val == '1')
                logger.info("RTL status retrieved from cookie: %s", is_rtl)

            if cookie_lan_id_hex and cookie_rtl_val:
                return lang_id_bytes , is_rtl

        # اگر کوکی نبود
        default_language = Language.query.filter_by(default=True).first()
        user_language = None

        if current_user.is_authenticated and current_user.language_id:
            user_language = Language.query.filter_by(id=current_user.language_id, is_active=True).first()

        active_language = user_language if user_language else default_language

        if not active_language:
            logger.warning("No active language found. Returning None.")
            return None , None
        lang_id_bytes = active_language.id
        logger.info("Active language retrieved from DB: %s", active_language)
        is_rtl = active_language.rtl
        logger.info("RTL status retrieved from DB: %s", is_rtl)

        if current_user.is_authenticated and lang_id_bytes:
            cookie_language_name = f"user_lang_{current_user.email}"
            cookie_rtl_name = f"user_rtl_{current_user.email}"

            # تبدیل بایت به هگز برای ذخیره در کوکی
            cookie_lan_id_hex = UnitUtils.bytes_to_hex(lang_id_bytes)

            @after_this_request
            def set_cookie(response):
                response.set_cookie(cookie_language_name, cookie_lan_id_hex)
                logger.info("Cookie '%s' set with hex value: %s", cookie_language_name, cookie_lan_id_hex)
                c_val = '1' if is_rtl else '0'
                response.set_cookie(cookie_rtl_name, c_val)
                logger.info("Cookie '%s' set with value: %s", cookie_rtl_name, c_val)
                return response
        # اگر کاربر لاگین نیست، نمی‌توان کوکی نوشت، پس صرفاً مقدار بایت را برمی‌گردانیم
        return lang_id_bytes , is_rtl

    except Exception as e:
        logger.exception("Error retrieving active language: %s", e)
        raise

def get_translation(context_key, original_value):
    """
    متد واحد برای دریافت ترجمه‌ها (لیبل‌های فرم و داده‌های دیتابیس)
    """
    try:
        # بررسی زبان کاربر یا زبان پیش‌فرض
        language_id,is_rtl = get_active_language()

        # اگر زبان انتخاب نشده بود، مقدار اصلی را بازگردان
        if not language_id:
            return original_value

        # بررسی ترجمه در دیتابیس
        translation = Translation.query.filter_by(key=original_value).first()
        if translation:
            translation_value = TranslationValue.query.filter_by(
                translation_id=translation.id,
                language_id=language_id
            ).first()
            if translation_value and translation_value.value:
                return translation_value.value

        return original_value

    except Exception as e:
        logger.error(f"Error fetching translation for key '{context_key}': {str(e)}")
        return original_value

def delete_language_cookies():
    """
    حذف کوکی‌های مربوط به زبان کاربر.
    """
    try:
        if current_user.is_authenticated:
            cookie_language_name = f"user_lang_{current_user.email}"
            cookie_rtl_name = f"user_rtl_{current_user.email}"

            @after_this_request
            def delete_cookies(response):
                response.delete_cookie(cookie_language_name)
                logger.info(f"Cookie '{cookie_language_name}' deleted.")
                response.delete_cookie(cookie_rtl_name)
                logger.info(f"Cookie '{cookie_rtl_name}' deleted.")
                return response
    except Exception as e:
        logger.error(f"Error deleting language cookies: {str(e)}")
        raise

def gettext(key):
    """
    متد کمکی برای ترجمه متن‌ها
    """
    if not key:
        return ''
    try:
        language_id, is_rtl = get_active_language()  # دریافت زبان فعال
        translation = Translation.get_by_key(key)
        if translation:
            value = TranslationValue.query.filter_by(
                translation_id=translation.id,
                language_id=language_id
            ).first()
            if value and value.value:
                return value.value
            logger.info(f"Translation not found for key: {key}")
        return key  # در صورت عدم وجود ترجمه، خود کلید نمایش داده می‌شود
    
    except Exception as e:
        logger.error(f"Error in gettext for key '{key}': {str(e)}")
        raise

