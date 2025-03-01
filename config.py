import os



class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default-secret-key')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')

        # 🔑 Microsoft Translator API Config
    MICROSOFT_TRANSLATOR_KEY = os.getenv('MICROSOFT_TRANSLATOR_KEY')
    MICROSOFT_TRANSLATOR_REGION = os.getenv('MICROSOFT_TRANSLATOR_REGION')


    if SQLALCHEMY_DATABASE_URI: 
        print (SQLALCHEMY_DATABASE_URI)
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    WTF_CSRF_ENABLED = True
