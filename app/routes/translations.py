from ..forms.translation_forms import LanguageForm,TranslationForm
from ..models import Language,Translation,TranslationValue
from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_required
from ..extensions import get_logger,UnitUtils,DBUtils,azure_translate
from ..services import scan_translations,scan_database,discover_forms,scan_form_labels,scan_flash_messages
from ..services import scan_validation_messages,delete_language_cookies

logger = get_logger('routes')
language_bp = Blueprint('translate', __name__)

@language_bp.context_processor
def inject_parent_menu():
    # بررسی آدرس فعلی و تعیین والد
    if '/translation' in request.path:
        return {'parent_menu': 'translations'}
    elif '/language/' in request.path:
        return {'parent_menu': 'languages'}

    return {'parent_menu': None}  # پیش‌فرض: منویی فعال نباشد


@language_bp.route('/languages', methods=['GET'])
@login_required
def list_languages():
    """نمایش لیست زبان‌ها"""
    try:
        languages = Language.get_all()
        form = LanguageForm()
        logger.info("Fetched all languages successfully.")
        return render_template('translate/languages.html', languages=languages, form=form)
    except Exception as e:
        logger.error(f"Error fetching languages: {e}")
        flash("An error occurred while fetching languages.", "danger")
        return redirect(url_for('auth.dashboard'))

@language_bp.route('/language', methods=['GET', 'POST'], defaults={'language_id': None})
@language_bp.route('/language/<string:language_id>', methods=['GET', 'POST'])
@login_required
def language(language_id):
    """
    افزودن یا ویرایش زبان
    اگر `language_id` وجود داشته باشد، ویرایش انجام می‌شود.
    اگر `language_id` وجود نداشته باشد، زبان جدید اضافه می‌شود.
    """
    if language_id:
        try:
            binary_id = UnitUtils.hex_to_bytes(language_id)  # تبدیل هگز به باینری
            logger.info(f"Fetching language with ID: {language_id})")
            language = Language.get_by_id(binary_id)
            if not language:
                logger.warning(f"Language with ID {language_id} not found.")
                flash("Language not found.", "warning")
                return redirect(url_for('translate.list_languages'))
            logger.info(f"Editing language: {language.code}")
        except Exception as e:
            logger.error(f"Invalid language ID: {language_id} - {str(e)}")
            flash("Invalid language ID.", "danger")
            return redirect(url_for('translate.list_languages'))
    else:
        language = None
        logger.info("Adding a new language.")

    form = LanguageForm(obj=language)

    if request.method == 'POST' and form.validate_on_submit():
        try:
            if language:
                logger.info(f"Updating language: {language.code}")
                language.name = form.name.data
                language.is_active = form.is_active.data
                language.rtl = form.rtl.data
                if language.save():
                    logger.info(f"Language {language.code} updated successfully.")
                    flash("Language updated successfully.", "success")
                else:
                    logger.error(f"Failed to update language: {language.code}")
                    flash("Failed to update language.", "danger")
            else:
                new_language = Language(
                    id=DBUtils.generate_uuid(),  # تولید UUID جدید
                    code=form.code.data,
                    name=form.name.data,
                    is_active=form.is_active.data
                )
                if new_language.save():
                    logger.info(f"Language {new_language.code} added successfully.")
                    flash("Language added successfully.", "success")
                else:
                    logger.error(f"Failed to add language: {new_language.code}")
                    flash("Failed to add language.", "danger")

            return redirect(url_for('translate.list_languages'))

        except Exception as e:
            logger.critical(f"Unexpected error in language route: {str(e)}", exc_info=True)
            flash("An unexpected error occurred.", "danger")

    return render_template('translate/language.html', form=form, language=language)

@language_bp.route('/language/delete/<language_id>', methods=['POST'])
@login_required
def delete_language(language_id):
    """حذف زبان به همراه تمام ترجمه‌های مرتبط"""
    try:
        # تبدیل شناسه از هگز به باینری
        language_id = UnitUtils.hex_to_bytes(language_id)
        language = Language.get_by_id(language_id)

        if not language:
            flash('Language not found.', 'danger')
            return redirect(url_for('translate.list_languages'))

        # استفاده از متد delete مدل Language
        success, message = Language.delete(language_id)

        if success:
            logger.info(f"Language deleted: {language.code} - {language.name}")
            flash(f"Language '{language.name}' and its related translations deleted successfully.", "success")
        else:
            flash(message, 'danger')  # نمایش پیام خطا برگشتی از مدل

    except Exception as e:
        logger.error(f"Error deleting language: {e}")
        flash("An error occurred while deleting the language.", "danger")

    return redirect(url_for('translate.list_languages'))

@language_bp.route('/language/set_default/<language_id>', methods=['POST'])
@login_required
def set_default_language(language_id):
    """
    تعیین یک زبان به عنوان زبان پیش‌فرض
    """
    try:
        # تبدیل شناسه از هگز به باینری
        binary_id = UnitUtils.hex_to_bytes(language_id)
        
        # فراخوانی متد مدل برای تنظیم زبان پیش‌فرض
        if Language.set_default(binary_id):
            delete_language_cookies()
            flash("Default language updated successfully.", "success")
            logger.info(f"Default language set for ID: {language_id}")
        else:
            flash("Error setting default language.", "danger")
            logger.warning(f"Failed to set default language for ID: {language_id}")

    except Exception as e:
        logger.error(f"Error setting default language: {str(e)}")
        flash("An unexpected error occurred while setting the default language.", "danger")

    return redirect(url_for('translate.list_languages'))

@language_bp.route('/translations', methods=['GET'])
@login_required
def list_translations():
    """
    نمایش لیست ترجمه‌ها به همراه دکمه اسکن
    """
    try:
        translations = Translation.get_all()  # استفاده از متد مدل
        languages = Language.get_all()
        form = TranslationForm()
        return render_template('translate/translations.html', 
                               translations=translations, 
                               languages=languages,form=form)
    except Exception as e:
        logger.error(f"Error fetching translations: {str(e)}")
        flash("An error occurred while fetching translations.", "danger")
        return redirect(url_for('auth.dashboard'))

@language_bp.route('/translations/scan', methods=['POST'])
@login_required
def scan_for_translations():
    """
    اجرای فرآیند اسکن برای شناسایی کلیدهای جدید از فایل‌ها، دیتابیس، و فرم‌ها
    """
    try:
        # اسکن فایل‌های HTML
        scan_translations()
        logger.info("File translation scan completed successfully.")

        # اسکن دیتابیس
        scan_database()
        logger.info("Database translation scan completed successfully.")

        # اسکن لیبل‌های فرم‌ها
        scan_form_labels()
        logger.info("Form labels scan completed successfully.")

        # اسکن خطاها
        scan_flash_messages()
        logger.info("Errors scan completed successfully.")

        scan_validation_messages()
        logger.info("Validation scan completed successfully.")        
        
        flash("Translation scan (files, database & forms) completed successfully.", "success")
    except Exception as e:
        logger.error(f"Error during translation scan: {str(e)}")
        flash("An error occurred while scanning translations.", "danger")

    return redirect(url_for('translate.list_translations'))

@language_bp.route('/translation/<string:translation_id>', methods=['GET', 'POST'])
@login_required
def manage_translation(translation_id):
    """
    نمایش و ویرایش ترجمه برای زبان‌های مختلف
    - GET: نمایش مقادیر ترجمه
    - POST: ذخیره تغییرات ترجمه
    """
    try:
        # تبدیل ID از هگز به باینری
        binary_id = UnitUtils.hex_to_bytes(translation_id)
        translation = Translation.get_by_id(binary_id)
        languages = [lang for lang in Language.get_all() if lang.code != 'en']

        form = TranslationForm(obj=translation)


        if request.method == 'POST':
            for language in languages:
                value = request.form.get(f'value_{language.id}')
                translation_value = TranslationValue.get_by_translation_and_language(translation.id, language.id)

                if translation_value:
                    translation_value.update_value(value)
                else:
                    TranslationValue.create(translation.id, language.id, value)

            flash("Translations updated successfully.", "success")
            return redirect(url_for('translate.list_translations'))

        return render_template('translate/manage_translation.html', translation=translation, 
                               languages=languages, form=form)

    except Exception as e:
        logger.error(f"Error managing translation: {str(e)}")
        flash("An error occurred while managing the translation.", "danger")
        return redirect(url_for('translate.list_translations'))

@language_bp.route('/translation/delete/<string:translation_id>', methods=['POST'])
@login_required
def delete_translation(translation_id):
    """
    حذف ترجمه بر اساس ID
    """
    try:
        # تبدیل ID از هگز به باینری
        binary_id = UnitUtils.hex_to_bytes(translation_id)
        translation = Translation.get_by_id(binary_id)

        if not translation:
            flash("Translation not found.", "danger")
            return redirect(url_for('translate.list_translations'))

        if Translation.delete(binary_id):
            logger.info(f"Translation deleted: {translation.key}")
            flash("Translation deleted successfully.", "success")
        else:
            flash("Error deleting translation.", "danger")

    except Exception as e:
        logger.error(f"Error deleting translation: {str(e)}")
        flash("An error occurred while deleting the translation.", "danger")

    return redirect(url_for('translate.list_translations'))

@language_bp.route('/translations/auto-translate', methods=['POST'])
@login_required
def auto_translate():
    """
    روت برای ترجمه خودکار کلیدهای بدون ترجمه با استفاده از Microsoft Translator
    """
    try:
        logger.info("Auto translation process started.")

        # دریافت همه زبان‌های فعال (غیر از انگلیسی)
        languages = Language.get_all()
        active_languages = [lang for lang in languages if lang.code != 'en' and lang.is_active]
        logger.info(f"Active languages fetched: {[lang.code for lang in active_languages]}")

        # دریافت همه کلیدهای ترجمه
        translations = Translation.get_all()
        logger.info(f"Total translations fetched: {len(translations)}")

        for translation in translations:
            logger.debug(f"Processing translation key: {translation.key}")
            for language in active_languages:
                logger.debug(f"Checking translation for language: {language.code}")

                # بررسی وجود ترجمه با استفاده از متد مدل
                existing_translation = TranslationValue.get_by_translation_and_language(
                    translation_id=translation.id,
                    language_id=language.id
                )

                if not existing_translation:
                    logger.info(f"No existing translation found for key '{translation.key}' in language '{language.code}'. Requesting translation...")

                    # درخواست ترجمه از Microsoft Translator
                    try:
                        translated_text = azure_translate(translation.key, language.code)
                        logger.info(f"Received translation for key '{translation.key}' in '{language.code}': {translated_text}")
                    except Exception as api_error:
                        logger.error(f"API error while translating key '{translation.key}' to '{language.code}': {api_error}")
                        continue

                    if translated_text:
                        # ذخیره ترجمه جدید با استفاده از متد مدل
                        new_translation = TranslationValue.create(
                            translation_id=translation.id,
                            language_id=language.id,
                            value=translated_text
                        )
                        if new_translation:
                            logger.info(f"Translation added for key '{translation.key}' in {language.code}.")
                        else:
                            logger.warning(f"Failed to save translation for key '{translation.key}' in {language.code}.")
                    else:
                        logger.warning(f"Translation API returned empty for key '{translation.key}' in {language.code}.")

        flash("Auto translation completed successfully.", "success")
        logger.info("Auto translation process completed successfully.")

    except Exception as e:
        logger.error(f"Error during auto translation: {str(e)}")
        flash("An error occurred during auto translation.", "danger")

    return redirect(url_for('translate.list_translations'))
