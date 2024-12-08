from flask import Flask, redirect, url_for, session, request, render_template, abort
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user, UserMixin
from requests_oauthlib import OAuth2Session

app = Flask(__name__)
app.secret_key = 'z[}{*Hw4Eb3`<.t(@5a&~r'  # جایگزین با یک کلید امن
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://username:password@localhost/yourdatabase'
db = SQLAlchemy(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# تنظیمات OAuth 2 گوگل
client_id = '640215854838-3nc3pdvsdg5c894jcofljaonj2fomm5g.apps.googleusercontent.com'
client_secret = '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'
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
redirect_uri = 'http://wlcomco.comco.ir/login/callback'
