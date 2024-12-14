import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hc4KmjgQDwRLpZaJUkN97G'
    SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://wlcomco_user:4314314522P%40ss@localhost/wlcomco_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
