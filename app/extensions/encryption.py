from cryptography.fernet import Fernet
import os


class Encryption:
    def __init__(self):
        # خواندن کلید از .env
        key = os.getenv('ENCRYPTION_KEY')
        if not key:
            raise ValueError("Encryption key not found in .env file")
        
        # تبدیل کلید به فرمت مناسب برای Fernet
        self.cipher = Fernet(key.encode())

    def encrypt(self, plain_text):
        """رمزنگاری مقدار ورودی"""
        encrypted_text = self.cipher.encrypt(plain_text.encode())
        return encrypted_text.decode()

    def decrypt(self, encrypted_text):
        """رمزگشایی مقدار رمز شده"""
        decrypted_text = self.cipher.decrypt(encrypted_text.encode())
        return decrypted_text.decode()
