from .form_translation_helper import get_translation
from flask import g
from ..extensions import get_logger


validation_messages = {
    'required': 'This field is required.',
    'invalid': 'Invalid value.',
    'email': 'Invalid email address.',
    'length': 'Field must be between %(min)d and %(max)d characters long.',
    'equal_to': 'Field must be equal to %(other_name)s.',
    'number_range': 'Number must be between %(min)s and %(max)s.',
    'regexp': 'Invalid input format.',
    'url': 'Invalid URL.',
    'uuid': 'Invalid UUID format.',
    'ip_address': 'Invalid IP address.',
    'any_of': 'Value must be one of: %(values)s.',
    'none_of': 'Value must not be any of: %(values)s.',
    'file_required': 'A file is required.',
    'file_allowed': 'Invalid file type. Allowed types: %(extensions)s.',
    'file_size': 'File size must be less than %(max_size)d KB.',
    'json': 'Invalid JSON format.',
    'multiple_of': 'Number must be a multiple of %(number)s.',
    'max_length': 'Field cannot be longer than %(max)s characters.',
    'min_length': 'Field must be at least %(min)s characters long.',
    'exact_length': 'Field must be exactly %(length)d characters long.',
    'max_value': 'Value cannot be greater than %(max)d.',
    'min_value': 'Value cannot be less than %(min)d.',
    'password_match':'Password and confirmation do not match',
    'email_already_registerd':'This email is already registered.',
    'old_password':'Old password is not correct.'
}
logger = get_logger('services')


def get_validation_error(key, **kwargs):
    """
    دریافت پیام اعتبارسنجی با ترجمه و قالب‌بندی اختیاری.
    """    
    
    message = validation_messages.get(key, 'Validation message not found.')
    translated_message = get_translation(
        context_key=key,  # تغییر به استفاده از کلید مستقیم
        original_value=message
    )

    try:
        formatted_message = translated_message % kwargs if kwargs else translated_message
    except (KeyError, ValueError) as e:
        logger.error(f"Error formatting translation message for '{key}': {e}")
        formatted_message = translated_message

    return formatted_message
