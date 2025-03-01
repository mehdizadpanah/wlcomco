import os
import re
from ..models import Translation,db
from ..extensions import get_logger
from sqlalchemy import text
import importlib.util
import inspect
from flask_wtf import FlaskForm
from app import forms  # مسیر پوشه forms
from .translation_config import TRANSLATABLE_FIELDS
from .validation_messages import validation_messages



logger = get_logger('services')

# الگوی Regex برای پیدا کردن کلیدهای ترجمه
TRANSLATION_KEY_PATTERN = re.compile(r"{{\s*(?:_|gettext)\(['\"](.+?)['\"]\)\s*}}")

# الگوی Regex برای پیدا کردن پیام‌های flash
FLASH_MESSAGE_PATTERN = re.compile(r"flash\s*\(\s*(['\"])(.*?)\1\s*,\s*(['\"])(.*?)\3")

# الگوی Regex برای پیدا کردن تایتل ها
LAZY_TITLE_PATTERN = re.compile(r"LazyTitle\s*\(\s*['\"](.+?)['\"]\s*\)")



def scan_translations():
    logger.info("Starting translation scan...")
    templates_dir = os.path.abspath('templates')

    for root, dirs, files in os.walk(templates_dir):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                logger.info(f"Scanning file: {file_path}")
                extract_translation_keys(file_path)

    logger.info("Translation scan completed.")

def extract_translation_keys(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        keys = re.findall(r"{{\s*(?:_|gettext)\s*\(\s*['\"](.*?)['\"]\s*\)\s*}}", content)
        context = os.path.basename(file_path).replace('.html', '')

        logger.info(f"Found keys in {file_path}: {keys}")

        for key in keys:
            translation = Translation.query.filter_by(key=key).first()

            if translation:
                translation.save(new_context=context)
            else:
                new_translation = Translation(key=key, context=context, source_type='template')
                new_translation.save()

    except Exception as e:
        logger.error(f"Error extracting translation keys from {file_path}: {str(e)}")

def save_translation_key(key,context):
    """
    ذخیره کلید ترجمه با استفاده از متد مدل Translation
    """
    try:
        existing_translation = Translation.get_by_key(key)
        if not existing_translation:
            new_translation = Translation(key=key, context=context)
            if new_translation.save():  # استفاده از متد save در مدل
                logger.info(f"Translation key '{key}' added successfully.")
            else:
                logger.warning(f"Failed to save translation key '{key}'.")
        else:
            logger.info(f"Translation key '{key}' already exists.")

    except Exception as e:
        logger.error(f"Error occurred while saving translation key '{key}': {str(e)}")

def scan_database():
    logger.info("Starting database scan for translations...")

    try:
        for table, fields in TRANSLATABLE_FIELDS.items():
            logger.info(f"Scanning table: {table}")

            query = text(f"SELECT id, {', '.join(fields)} FROM {table}")
            results = db.session.execute(query).fetchall()

            for row in results:
                for field in fields:
                    value = getattr(row, field, None)
                    if not value:
                        continue

                    context = f"{table}.{field}"
                    existing_translation = Translation.query.filter_by(key=value).first()

                    if existing_translation:
                        existing_contexts = set(filter(None, existing_translation.context.split(',')))
                        existing_contexts.add(context)
                        existing_translation.context = ','.join(sorted(existing_contexts))
                        db.session.commit()
                        logger.info(f"Context '{context}' added to existing translation '{value}'.")
                    else:
                        new_translation = Translation(key=value, context=context, source_type='database')
                        db.session.add(new_translation)
                        db.session.commit()
                        logger.info(f"New translation added: '{value}' with context '{context}'.")

        logger.info("Database scan completed successfully.")
        return True

    except Exception as e:
        logger.error(f"Error occurred during database scan: {str(e)}")
        db.session.rollback()
        return False

def discover_forms():
    """
    اسکن پوشه forms برای یافتن تمام کلاس‌های فرم که از FlaskForm ارث‌بری کرده‌اند.
    """
    forms_directory = os.path.dirname(forms.__file__)
    discovered_forms = []
    try:
        for root, dirs, files in os.walk(forms_directory):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    module_path = os.path.join(root, file)
                    module_name = module_path.replace(forms_directory, 'app.forms').replace('/', '.').replace('\\', '.').rstrip('.py')

                    # وارد کردن داینامیک ماژول
                    spec = importlib.util.spec_from_file_location(module_name, module_path)
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)

                    # پیدا کردن کلاس‌های فرم
                    for name, obj in inspect.getmembers(module, inspect.isclass):
                        if issubclass(obj, FlaskForm) and obj != FlaskForm:
                            discovered_forms.append(obj)

        logger.info("Form discovery and translation scan completed successfully.")
        return discovered_forms

    except Exception as e:
        logger.error(f"Error occurred during form discovery: {str(e)}")
        db.session.rollback()
        return []

def scan_form_labels():
    logger.info("Starting form labels scan from form files (as text)...")
    forms_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'forms'))
    
    try:
        for root, dirs, files in os.walk(forms_directory):
            for file in files:
                if file.endswith('.py') and not file.startswith('__'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # پیدا کردن تمام موارد LazyTitle("...")
                    keys = re.findall(LAZY_TITLE_PATTERN, content)
                    context = os.path.splitext(file)[0]
                    
                    logger.info(f"Found keys in {file_path}: {keys}")
                    
                    for key in keys:
                        # چک کردن وجود ترجمه در دیتابیس
                        existing_translation = Translation.query.filter_by(key=key).first()
                        if existing_translation:
                            existing_contexts = set(filter(None, existing_translation.context.split(',')))
                            if context not in existing_contexts:
                                existing_contexts.add(context)
                                existing_translation.context = ' , '.join(sorted(existing_contexts))
                                db.session.commit()
                                logger.info(f"Updated context for '{key}': {existing_translation.context}")
                        else:
                            new_translation = Translation(key=key, context=context, source_type='form')
                            db.session.add(new_translation)
                            db.session.commit()
                            logger.info(f"New translation added: '{key}' with context '{context}' and source_type 'form'")
        logger.info("Form labels scan from text completed successfully.")
        return True
    except Exception as e:
        logger.error(f"Error occurred during form labels scan from text: {str(e)}")
        db.session.rollback()
        return False

def scan_flash_messages():
    """
    اسکن پیام‌های فلش از فایل‌های پایتون در پروژه
    """
    logger.info("Starting flash messages scan...")

    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))  # مسیر ریشه پروژه

    for root, dirs, files in os.walk(project_root):
        for file in files:
            if file.endswith('.py'):
                file_path = os.path.join(root, file)
                logger.info(f"Scanning file: {file_path}")
                extract_flash_messages(file_path)

    logger.info("Flash messages scan completed successfully.")

def extract_flash_messages(file_path):
    """
    استخراج پیام‌های فلش از یک فایل پایتون
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()

        matches = re.findall(FLASH_MESSAGE_PATTERN, content)

        for match in matches:
            message = match[1]  # پیام اصلی
            context = os.path.basename(file_path)  # فقط نام فایل به عنوان کانتکست

            existing_translation = Translation.query.filter_by(key=message).first()

            if existing_translation:
                existing_contexts = set(filter(None, existing_translation.context.split(' , ')))
                if context not in existing_contexts:
                    existing_contexts.add(context)
                    existing_translation.context = ' , '.join(sorted(existing_contexts))
                    existing_translation.source_type = 'notice'  # تغییر از error به notice
                    db.session.commit()
                    logger.info(f"Context '{context}' added to existing flash message '{message}'.")
            else:
                new_translation = Translation(key=message, context=context, source_type='notice')
                db.session.add(new_translation)
                db.session.commit()
                logger.info(f"New flash message added: '{message}' with context '{context}'")

    except Exception as e:
        logger.error(f"Error extracting flash messages from {file_path}: {str(e)}")

def scan_validation_messages():
    """
    اسکن پیام‌های ولیدیشن و ذخیره به‌عنوان ترجمه.
    """
    logger.info("Starting validation messages scan...")

    try:
        for key, message in validation_messages.items():
            translation = Translation(key=message, source_type='validation')

            # استفاده از متد save برای درج یا به‌روزرسانی
            if translation.save(new_context=key):
                logger.info(f"Validation message '{message}' saved with context '{key}'")
            else:
                logger.error(f"Failed to save validation message '{message}'")

        logger.info("Validation messages scan completed successfully.")
        return True

    except Exception as e:
        logger.error(f"Error during validation messages scan: {str(e)}")
        return False
