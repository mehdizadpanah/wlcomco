from dotenv import load_dotenv
import os
import sys



sys.path.insert(0, '/var/www/wlcomco')

dotenv_path = '/var/www/wlcomco/.env'
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)

os.environ['FLASK_APP'] = 'app'  # اضافه کردن متغیر محیطی

from app import create_app

application = create_app()
