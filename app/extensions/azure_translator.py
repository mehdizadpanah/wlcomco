import requests
from flask import current_app
from ..extensions import get_logger

logger = get_logger('extentions')

def azure_translate(text, target_language):
    """
    ترجمه متن با استفاده از Microsoft Translator API
    :param text: متنی که باید ترجمه شود
    :param target_language: کد زبان مقصد (مثلاً 'fa' برای فارسی)
    :return: متن ترجمه‌شده یا متن اصلی در صورت خطا
    """
    try:
        api_key = current_app.config.get('MICROSOFT_TRANSLATOR_KEY')
        region = current_app.config.get('MICROSOFT_TRANSLATOR_REGION')
        endpoint = "https://api.cognitive.microsofttranslator.com/translate"
        api_version = "3.0"

        if not api_key or not region:
            logger.error("Microsoft Translator API key or region is missing.")
            return text

        params = {
            'api-version': api_version,
            'to': target_language
        }

        headers = {
            'Ocp-Apim-Subscription-Key': api_key,
            'Ocp-Apim-Subscription-Region': region,
            'Content-Type': 'application/json'
        }

        body = [{'text': text}]

        response = requests.post(endpoint, params=params, headers=headers, json=body)
        response.raise_for_status()

        translation_result = response.json()
        translated_text = translation_result[0]['translations'][0]['text']

        return translated_text

    except Exception as e:
        logger.error(f"Translation error: {str(e)}")
        raise e