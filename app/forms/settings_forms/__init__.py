from .channel_settings_form import ChannelSettingsForm
from .notification_form import NotificationForm
from .smtp_settings_form import SMTPSettingsForm
from .settings_form import SettingsForm
from .general_settings_form import GeneralSettingsForm
from .cache_settings_form import CacheServerForm
from .file_server_form import FileServerForm

# لیستی از فرم‌ها برای استفاده در کل پروژه
__all__ = ['ChannelSettingsForm','NotificationForm','SMTPSettingsForm',
           'SettingsForm','GeneralSettingsForm','CacheServerForm','FileServerForm']
