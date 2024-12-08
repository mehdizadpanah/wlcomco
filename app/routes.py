from flask import Blueprint, render_template, redirect, url_for, session, request
from flask_login import login_user, logout_user, login_required, current_user
from . import db, login_manager
from .models import User
from requests_oauthlib import OAuth2Session

routes = Blueprint('routes', __name__)  # تعریف Blueprint

client_id = '640215854838-3nc3pdvsdg5c894jcofljaonj2fomm5g.apps.googleusercontent.com'
client_secret = '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'
authorization_base_url = 'https://accounts.google.com/o/oauth2/auth'
token_url = 'https://accounts.google.com/o/oauth2/token'
redirect_uri = 'https://wlcomco.comco.ir/login/callback'

@routes.route('/')  # استفاده از routes برای مسیرها
def index():
    return "Welcome to the Flask Application!"

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@routes.route('/login')
def login():
    google = OAuth2Session(client_id, redirect_uri=redirect_uri, scope=['email', 'profile'])
    authorization_url, state = google.authorization_url(
        authorization_base_url,
        access_type='offline', prompt='select_account')
    session['oauth_state'] = state
    return redirect(authorization_url)

@routes.route('/login/callback')
def callback():
    google = OAuth2Session(client_id, state=session['oauth_state'], redirect_uri=redirect_uri)
    token = google.fetch_token(token_url, client_secret=client_secret,
                               authorization_response=request.url)

    user_info = google.get('https://www.googleapis.com/oauth2/v1/userinfo').json()

    user = User.query.filter_by(email=user_info['email']).first()
    if not user:
        user = User(email=user_info['email'], name=user_info['name'])
        db.session.add(user)
        db.session.commit()

    login_user(user)
    return redirect(url_for('routes.dashboard'))

@routes.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.name)

@routes.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('routes.login'))
