from ..forms.general_settings_forms import ChannelSettingsForm,NotificationForm,SMTPSettingsForm
import os
from ..models import Setting,Notification,db
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify,flash
from flask_login import login_required
from ..logging_config import get_logger

# تعریف logger
logger = get_logger(__name__)


# تعریف Blueprint
general_settings_bp = Blueprint('general_settings', __name__, url_prefix='/general_settings')

# تعریف یک context_processor برای تعیین والد منو
@general_settings_bp.context_processor
def inject_parent_menu():
    # بررسی آدرس فعلی و تعیین والد
    if '/smtp_settings' in request.path:
        return {'parent_menu': 'channel_settings'}
    elif '/notification/' in request.path:
        return {'parent_menu': 'notifications'}
    return {'parent_menu': None}  # پیش‌فرض: منویی فعال نباشد



@general_settings_bp.route('/channel_settings', methods=['GET', 'POST'])
@login_required
def channel_settings():
    form = ChannelSettingsForm()


    if request.method == 'GET':
        # لود تنظیمات موجود
        form.smtp_host.data = Setting.get_setting('smtp_host', '')
        form.smtp_port.data = Setting.get_setting('smtp_port', '')
        form.smtp_username.data = Setting.get_setting('smtp_username', '')
        form.smtp_from.data = Setting.get_setting('smtp_from', '')
        form.smtp_password.data = Setting.get_setting('smtp_password', '')
        form.smtp_security.data = Setting.get_setting('smtp_security', '')


    return render_template('general_settings/channel_settings.html', form=form)



@general_settings_bp.route('/smtp_settings', methods=['GET', 'POST'])
@login_required
def smtp_settings():
    form = SMTPSettingsForm()
    if request.method=='POST':
        if form.validate_on_submit():
            Setting.set_setting('smtp_host', form.smtp_host.data)
            Setting.set_setting('smtp_port', form.smtp_port.data)
            Setting.set_setting('smtp_username', form.smtp_username.data)
            if form.smtp_password.data!= "******":
                Setting.set_setting('smtp_password', form.smtp_password.data)
            Setting.set_setting('smtp_security', form.smtp_security.data)
            Setting.set_setting('smtp_from', form.smtp_from.data)

            flash('SMTP settings updated successfully.', 'success')
            return redirect(url_for('general_settings.channel_settings'))
    if request.method=='GET':
        # لود تنظیمات موجود
        form.smtp_host.data = Setting.get_setting('smtp_host', '')
        form.smtp_port.data = Setting.get_setting('smtp_port', '')
        form.smtp_username.data = Setting.get_setting('smtp_username', '')
        form.smtp_password.data = Setting.get_setting('smtp_password', '')
        form.smtp_security.data = Setting.get_setting('smtp_security', '')
        form.smtp_from.data = Setting.get_setting('smtp_from', '')


    return render_template('general_settings/smtp_settings.html', form=form)

# لیست نوتیفیکیشن‌ها
@general_settings_bp.route('/notifications', methods=['GET'])
@login_required
def notifications():
    notifications = Notification.get_notifications()
    return render_template('general_settings/notifications.html', notifications=notifications)


@general_settings_bp.route('/notification/<int:notification_id>', methods=['GET','POST'])
@login_required
def notification(notification_id):
    notification = Notification.query.get_or_404(notification_id)
    form = NotificationForm(obj=notification)

        # دریافت نوتیفیکیشن بر اساس ID
    if notification_id is None:
        flash("Notification ID is required for editing.", "danger")
        return redirect(url_for('general_settings.notifications'))

    if request.method == 'POST':
        # مدیریت ارسال فرم (بدون نیاز به notification_id)
        if form.validate_on_submit():
            # notification_id = request.form.get("id")  # دریافت ID از فرم
            notification = Notification.query.get_or_404(notification_id)

            # به‌روزرسانی مقادیر نوتیفیکیشن
            form.populate_obj(notification)
            db.session.commit()
            flash('Notification updated successfully!', 'success')
            return redirect(url_for('general_settings.notifications'))

    return render_template('general_settings/notification.html',form=form,notification=notification)
