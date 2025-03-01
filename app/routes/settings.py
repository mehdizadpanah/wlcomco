from ..forms.settings_forms import ChannelSettingsForm,NotificationForm,SMTPSettingsForm,SettingsForm
from ..forms.settings_forms import GeneralSettingsForm,CacheServerForm,FileServerForm
from ..models import Setting,Notification,db,CacheServer,FileServer
from flask import Blueprint, render_template, redirect, url_for, request, flash
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
    elif '/general_settings' in request.path:
        return {'parent_menu': 'settings'}
    elif '/cache_server' in request.path:
        return {'parent_menu': 'cache_server'}
    elif '/file_server' in request.path:
        return {'parent_menu': 'file_server'}


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

@settings_bp.route('/cache_servers', methods=['GET'])
@login_required
def cache_servers():
    """
    نمایش فهرست سرورهای کش
    """
    form = CacheServerForm()
    logger.info("Cache servers list endpoint accessed.")
    try:
        servers = CacheServer.get_all()  # متد کمکی در مدل برای واکشی همه رکوردها
        return render_template('settings/cache_servers.html', cache_servers=servers,form=form)
    except Exception as e:
        logger.critical(f"Unexpected error in cache_servers route: {str(e)}")
        flash("An unexpected error occurred while loading cache servers list. Please try again later.", "danger")
        return redirect(url_for('settings.settings'))

@settings_bp.route('/cache_server', methods=['GET', 'POST'])
@settings_bp.route('/cache_server/<string:server_id>', methods=['GET', 'POST'])
@login_required
def cache_server(server_id=None):
    """
    ایجاد یا ویرایش یک سرور کش
    """
    logger.info("Cache server endpoint accessed.")
    try:
        if server_id:
            logger.info(f"Editing cache server with ID: {server_id}")
            server = CacheServer.get_by_id(server_id)
            if not server:
                logger.warning(f"Cache server not found for ID: {server_id}")
                flash("Cache server not found.", "warning")
                return redirect(url_for('settings.cache_servers'))
            form = CacheServerForm(obj=server)
            if request.method == 'GET':
                form.password.data = "******" if server.password else ""
        else:
            logger.info("Creating a new cache server.")
            server = CacheServer()
            form = CacheServerForm()

        if form.validate_on_submit():
            logger.info("Form validated successfully.")
            form.populate_obj(server)

            if server.save():
                flash("Cache server saved successfully.", "success")
                logger.info(f"Cache server {'updated' if server_id else 'added'} successfully.")
                return redirect(url_for('settings.cache_servers'))
            else:
                logger.error("Failed to save cache server changes.")
                flash("Failed to save cache server changes. Please try again.", "danger")
        else:
            if request.method == 'POST':
                logger.warning(f"Form validation errors: {form.errors}")

        # رندر تمپلیت جزئیات سرور کش
        return render_template('settings/cache_server.html', form=form, cache_server_id=server_id)

    except Exception as e:
        logger.critical(f"Unexpected error in cache_server route for ID {server_id}: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('settings.cache_servers'))


@settings_bp.route('/cache_server/<string:server_id>/delete', methods=['POST'])
@login_required
def delete_cache_server(server_id):
    """
    حذف یک سرور کش
    """
    logger.info(f"Delete cache server endpoint accessed for ID: {server_id}")
    try:
        server = CacheServer.get_by_id(server_id)
        if not server:
            logger.warning(f"Cache server not found for ID: {server_id}")
            flash("Cache server not found.", "warning")
            return redirect(url_for('settings.cache_servers'))

        if server.delete():
            flash("Cache server deleted successfully.", "success")
            logger.info(f"Cache server {server_id} deleted successfully.")
        else:
            flash("Failed to delete cache server.", "danger")
            logger.error(f"Failed to delete cache server {server_id} from the database.")

        return redirect(url_for('settings.cache_servers'))

    except Exception as e:
        logger.critical(f"Unexpected error in delete_cache_server route: {str(e)}")
        flash("An unexpected error occurred while deleting cache server. Please try again later.", "danger")
        return redirect(url_for('settings.cache_servers'))

@settings_bp.route('/file_servers', methods=['GET'])
@login_required
def file_servers():
    """
    نمایش لیست سرورهای فایل
    """
    logger.info("Accessing file servers list.")
    form = FileServerForm()
    try:
        servers = FileServer.get_all()
        return render_template('settings/file_servers.html', file_servers=servers, form=form)
    except Exception as e:
        logger.critical(f"Unexpected error in file_servers route: {str(e)}")
        flash("An unexpected error occurred while loading file servers list. Please try again later.", "danger")
        return redirect(url_for('settings.settings'))


@settings_bp.route('/file_server', methods=['GET', 'POST'])
@settings_bp.route('/file_server/<string:server_id>', methods=['GET', 'POST'])
@login_required
def file_server(server_id=None):
    """
    ایجاد یا ویرایش یک سرور فایل
    """
    try:
        if server_id:
            logger.info(f"Editing file server with ID: {server_id}")
            server = FileServer.get_by_id(server_id)
            if not server:
                logger.warning(f"File server not found for ID: {server_id}")
                flash("File server not found.", "warning")
                return redirect(url_for('settings.file_servers'))
            form = FileServerForm(obj=server)
            if request.method == 'GET':
                form.password.data = "******" if server.password else ""
        else:
            logger.info("Creating a new file server.")
            server = FileServer()
            form = FileServerForm()

        if form.validate_on_submit():
            logger.info("Form validated successfully.")
            form.populate_obj(server)

            if server.save():
                flash("File server saved successfully.", "success")
                logger.info(f"File server {'updated' if server_id else 'added'} successfully.")
                return redirect(url_for('settings.file_servers'))
            else:
                logger.error("Failed to save file server changes.")
                flash("Failed to save file server changes. Please try again.", "danger")
        else:
            if request.method == 'POST':
                if form.validate_on_submit():
                    logger.info("Form validated successfully.")

                    # به‌روزرسانی اطلاعات شیء مدل بر اساس ورودی‌های فرم
                    form.populate_obj(server)

                    # ذخیره در دیتابیس
                    if server.save():
                        flash("File server saved successfully.", "success")
                        logger.info(f"File server {'updated' if server_id else 'added'} successfully.")
                        return redirect(url_for('settings.file_servers'))
                    else:
                        logger.error("Failed to save file server changes.")
                        flash("Failed to save file server changes. Please try again.", "danger")

                else:
                    logger.warning(f"Form validation errors: {form.errors}")

        return render_template('settings/file_server.html', form=form, server_id=server_id)

    except Exception as e:
        logger.critical(f"Unexpected error in file_server route for ID {server_id}: {str(e)}")
        flash("An unexpected error occurred. Please try again later.", "danger")
        return redirect(url_for('settings.file_servers'))


@settings_bp.route('/file_server/<string:server_id>/delete', methods=['POST'])
@login_required
def delete_file_server(server_id):
    """
    حذف یک سرور فایل
    """
    logger.info(f"Delete file server endpoint accessed for ID: {server_id}")
    try:
        server = FileServer.get_by_id(server_id)
        if not server:
            logger.warning(f"File server not found for ID: {server_id}")
            flash("File server not found.", "warning")
            return redirect(url_for('settings.file_servers'))

        if server.delete():
            flash("File server deleted successfully.", "success")
            logger.info(f"File server {server_id} deleted successfully.")
        else:
            flash("Failed to delete file server.", "danger")
            logger.error(f"Failed to delete file server {server_id} from the database.")

        return redirect(url_for('settings.file_servers'))

    except Exception as e:
        logger.critical(f"Unexpected error in delete_file_server route: {str(e)}")
        flash("An unexpected error occurred while deleting file server. Please try again later.", "danger")
        return redirect(url_for('settings.file_servers'))




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

