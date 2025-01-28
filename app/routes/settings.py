from ..forms.settings_forms import ChannelSettingsForm,NotificationForm,SMTPSettingsForm,SettingsForm
from ..forms.settings_forms import GeneralSettingsForm
import os
from ..models import Setting,Notification,db
from flask import Blueprint, render_template, redirect, url_for, session, request, flash
from flask_login import login_required
from ..extensions import get_logger,ModelUtils

# تعریف Blueprint
settings_bp = Blueprint('settings', __name__)
logger = get_logger('routes')

# تعریف یک context_processor برای تعیین والد منو
@settings_bp.context_processor
def inject_parent_menu():
    # بررسی آدرس فعلی و تعیین والد
    if '/smtp_settings' in request.path:
        return {'parent_menu': 'channel_settings'}
    elif '/notification/' in request.path:
        return {'parent_menu': 'notifications'}
    return {'parent_menu': None}  # پیش‌فرض: منویی فعال نباشد


@settings_bp.route('/settings', methods=['GET'])
@login_required
def settings():
    """
    متد نمایش تنظیمات عمومی
    """
    logger.info(f"Settings endpoint accessed.")
    form = SettingsForm()

    try:
        if request.method == 'GET':
            logger.info("Loading general settings form.")
            load_settings(form)

        logger.info("Rendering settings page.")
        return render_template('settings/settings.html', form=form)

    except Exception as e:
        logger.critical(f"Unexpected error in settings route: {str(e)}")
        flash("An unexpected error occurred while loading settings. Please try again later.", "danger")
        return redirect(url_for('settings.settings'))


@settings_bp.route('/general_settings', methods=['GET', 'POST'])
@login_required
def general_settings():
    """
    متد تنظیمات عمومی برنامه
    """
    logger.info("General settings endpoint accessed.")
    form = GeneralSettingsForm()

    try:
        if request.method == 'GET':
            logger.info("Loading general settings form.")
            load_general_settings(form)

        if request.method == 'POST':
            logger.info("POST request received for general settings.")
            if form.validate_on_submit():
                logger.info("Form validated successfully. Saving general settings.")
                save_general_settings(form)
                flash(
                    'General settings updated successfully.<br>'
                    'If you have changed the application title, please <strong>restart the Apache server</strong> to apply the changes.',
                    'success'
                )
                logger.info("General settings updated and saved successfully.")
                return redirect(url_for('settings.settings'))

            if form.errors:
                logger.warning(f"Form validation errors: {form.errors}")

        logger.info("Rendering general settings page.")
        return render_template('settings/general_settings.html', form=form)

    except Exception as e:
        logger.critical(f"Unexpected error in general_settings route: {str(e)}")
        flash("An unexpected error occurred while processing general settings. Please try again later.", "danger")
        return redirect(url_for('settings.settings'))


@settings_bp.route('/channel_settings', methods=['GET'])
@login_required
def channel_settings():
    """
    متد برای نمایش تنظیمات کانال‌ها.
    """
    logger.info("Channel settings endpoint (GET) accessed.")
    form = ChannelSettingsForm()

    try:
        # لود تنظیمات کانال‌ها
        logger.info("Loading channel settings into the form.")
        load_channel_settings(form)

        # نمایش صفحه تنظیمات کانال‌ها
        logger.info("Rendering channel settings page.")
        return render_template('settings/channel_settings.html', form=form)

    except Exception as e:
        # مدیریت خطاهای غیرمنتظره
        logger.critical(f"Unexpected error in channel_settings (GET): {str(e)}")
        flash("An unexpected error occurred while loading channel settings. Please try again later.", "danger")
        return redirect(url_for('settings.settings'))


@settings_bp.route('/smtp_settings', methods=['GET', 'POST'])
@login_required
def smtp_settings():
    """
    متد برای مدیریت تنظیمات SMTP.
    """
    logger.info("SMTP settings endpoint accessed.")
    form = SMTPSettingsForm()

    try:
        if request.method == 'GET':
            # بارگذاری تنظیمات SMTP در فرم
            logger.info("Loading SMTP settings into the form.")
            load_smtp_settings(form)

        if request.method == 'POST':
            logger.info("POST request received for SMTP settings.")
            if form.validate_on_submit():
                # ذخیره تنظیمات SMTP
                logger.info("SMTP form validated successfully. Saving settings.")
                save_smtp_settings(form)
                flash('SMTP settings updated successfully.', 'success')
                logger.info("SMTP settings updated successfully.")
                return redirect(url_for('settings.channel_settings'))

            # مدیریت خطاهای اعتبارسنجی فرم
            if form.errors:
                logger.warning(f"Form validation errors: {form.errors}")

        # رندر صفحه تنظیمات SMTP
        logger.info("Rendering SMTP settings page.")
        return render_template('settings/smtp_settings.html', form=form)

    except Exception as e:
        # مدیریت خطاهای غیرمنتظره
        logger.critical(f"Unexpected error in smtp_settings: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('settings.channel_settings'))


# لیست نوتیفیکیشن‌ها
@settings_bp.route('/notifications', methods=['GET'])
@login_required
def notifications():
    """
    متد برای نمایش لیست نوتیفیکیشن‌ها.
    """
    logger.info("Notifications endpoint accessed.")

    try:
        # بازیابی لیست نوتیفیکیشن‌ها از پایگاه داده
        notifications = Notification.get_all()
        logger.info(f"Loaded {len(notifications)} notifications from the database.")

        # رندر صفحه نمایش نوتیفیکیشن‌ها
        return render_template('settings/notifications.html', notifications=notifications)

    except Exception as e:
        # مدیریت خطاهای غیرمنتظره
        logger.critical(f"Unexpected error in notifications: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('settings.settings'))


@settings_bp.route('/notification/<notification_name>', methods=['GET', 'POST'])
@login_required
def notification(notification_name):
    """
    متد مدیریت نوتیفیکیشن‌ها برای مشاهده و ویرایش.
    """
    logger.info(f"Notification endpoint accessed for notification ID: {notification_name}")

    try:
        # دریافت نوتیفیکیشن بر اساس ID
        notification = Notification.get_by_name(notification_name)
        if not notification:
            logger.warning(f"Notification {notification_name} not found.")
            flash("Notification not found.", "danger")
            return redirect(url_for('settings.notifications'))

        logger.info(f"Notification loaded with ID: {notification_name}")

        # ذخیره اطلاعات اولیه قبل از تغییر
        original_data = ModelUtils.to_dict(notification)

        form = NotificationForm(obj=notification)

        if request.method == 'POST':
            logger.info(f"POST request received for notification ID: {notification_name}")

            if form.validate_on_submit():
                logger.info(f"Form validated successfully for notification ID: {notification_name}")

                # به‌روزرسانی مقادیر نوتیفیکیشن
                form.populate_obj(notification)

                # ارسال اطلاعات قبل از تغییر به همراه شیء به متد save
                notification.save(original_data)

                logger.info(f"Notification ID {notification_name} updated successfully.")
                flash('Notification updated successfully!', 'success')
                return redirect(url_for('settings.notifications'))

            if form.errors:
                logger.warning(f"Form validation errors for notification ID {notification_name}: {form.errors}")

        return render_template('settings/notification.html', form=form, notification=notification)

    except Exception as e:
        # مدیریت خطاهای غیرمنتظره
        logger.critical(f"Unexpected error in notification route for ID {notification_name}: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('settings.notifications'))


def load_general_settings(form):
        form.app_title.data = Setting.get_by_name('app_title', '')
        form.logging_level.data = Setting.get_by_name('logging_level', '')
        form.logging_file_retention.data = Setting.get_by_name('logging_file_retention','')
        form.logging_file_size.data = Setting.get_by_name('logging_file_size','')

def save_general_settings(form):
    """
    ذخیره تنظیمات عمومی با استفاده از متد `save_settings` در مدل
    """
    logger.info("Saving general settings...")
    updates = {
        "app_title": form.app_title.data,
        "logging_level": form.logging_level.data,
        "logging_file_retention": form.logging_file_retention.data,
        "logging_file_size": form.logging_file_size.data
    }
    if Setting.save_bulk(updates):
        logger.info("General settings updated successfully.")
        return True
    else:
        logger.error("Failed to update general settings.")
        return False

def load_settings(form):
    load_general_settings(form)

def load_channel_settings(form):
    load_smtp_settings(form)

def load_smtp_settings(form):
    form.smtp_host.data = Setting.get_by_name('smtp_host', '')
    form.smtp_port.data = Setting.get_by_name('smtp_port', '')
    form.smtp_username.data = Setting.get_by_name('smtp_username', '')
    form.smtp_password.data = Setting.get_by_name('smtp_password', '')
    form.smtp_security.data = Setting.get_by_name('smtp_security', '')
    form.smtp_from.data = Setting.get_by_name('smtp_from', '')

def save_smtp_settings(form):
    """
    ذخیره تنظیمات SMTP با استفاده از متد `save_settings` در مدل
    """
    logger.info("Saving SMTP settings...")
    updates = {
        "smtp_host": form.smtp_host.data,
        "smtp_port": form.smtp_port.data,
        "smtp_username": form.smtp_username.data,
        "smtp_password": form.smtp_password.data ,
        "smtp_security": form.smtp_security.data,
        "smtp_from": form.smtp_from.data
    }
    # حذف مقادیر None
    updates = {k: v for k, v in updates.items() if v is not None}

    if Setting.save_bulk(updates):
        logger.info("SMTP settings updated successfully.")
        return True
    else:
        logger.error("Failed to update SMTP settings.")
        return False
