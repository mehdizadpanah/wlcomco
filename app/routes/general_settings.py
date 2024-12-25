from ..forms.general_settings_forms import ChannelsForm
import os
from ..models import Setting,db
from flask import Blueprint, render_template, redirect, url_for, session, request, jsonify,flash
from flask_login import login_required
from ..logging_config import get_logger

# تعریف logger
logger = get_logger(__name__)

# تعریف Blueprint
general_settings_bp = Blueprint('general_settings', __name__, url_prefix='/general_settings')

@general_settings_bp.route('/channels', methods=['GET', 'POST'])
@login_required
def channels():
    form = ChannelsForm()

    if request.method == "POST":
        if form.validate_on_submit():
            Setting.set_setting('smtp_host', form.smtp_host.data)
            Setting.set_setting('smtp_port', form.smtp_port.data)
            Setting.set_setting('smtp_username', form.smtp_username.data)
            if form.smtp_password.data!= "******":
                Setting.set_setting('smtp_password', form.smtp_password.data)
            Setting.set_setting('smtp_security', form.smtp_security.data)

            flash('SMTP settings updated successfully.', 'success')
            return redirect(url_for('general_settings.channels'))
    if request.method == 'GET':
        # لود تنظیمات موجود
        form.smtp_host.data = Setting.get_setting('smtp_host', '')
        form.smtp_port.data = Setting.get_setting('smtp_port', '')
        form.smtp_username.data = Setting.get_setting('smtp_username', '')
        form.smtp_password.data = Setting.get_setting('smtp_password', '')
        form.smtp_security.data = Setting.get_setting('smtp_security', '')


    return render_template('general_settings/channels.html', form=form)
