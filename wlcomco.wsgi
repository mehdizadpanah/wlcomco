import os
import sys

sys.path.insert(0, '/var/www/wlcomco')

os.environ['FLASK_APP'] = 'app'  # اضافه کردن متغیر محیطی

from app import create_app

os.environ['SECRET_KEY'] = 'hc4KmjgQDwRLpZaJUkN97G'

application = create_app()
