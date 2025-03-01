from cryptography.fernet import Fernet
from ..extensions.logging_client import get_logger
import os


logger = get_logger('extentions')

class Encryption:

    @staticmethod
    def encrypt(plain_text):
        """رمزنگاری مقدار ورودی"""
        try:
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                logger.error("Encryption key not found in .env file")
                
            cipher = Fernet(key.encode())
            encrypted_text = cipher.encrypt(plain_text.encode())
            logger.info("Encrypting data")
            return encrypted_text.decode()
        
        except Exception as e:
            logger.error(f"Encryption error: {str(e)}")
            raise e


    @staticmethod
    def decrypt(encrypted_text):
        """رمزگشایی مقدار رمز شده"""
        try:
            key = os.getenv('ENCRYPTION_KEY')
            if not key:
                logger.error("Encryption key not found in .env file")
            cipher = Fernet(key.encode())
            decrypted_text = cipher.decrypt(encrypted_text.encode())
            logger.info("Decrypting data")
            return decrypted_text.decode()
        
        except Exception as e:
            logger.error(f"Decryption error: {str(e)}")
            raise e
