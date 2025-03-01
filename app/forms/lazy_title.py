from ..services.form_translation_helper import get_translation

class LazyTitle:
    def __init__(self, translation_key):
        self.translation_key = translation_key

    def __html__(self):
        # در هنگام رندر HTML، خود شیء LazyTitle را برگردانیم
        return self

    def __str__(self):
        # زمانی که به‌صورت صریح به رشته تبدیل می‌شود، ترجمه را برگردانیم
        return get_translation(self.translation_key, self.translation_key)
