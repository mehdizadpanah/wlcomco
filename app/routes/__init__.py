from flask import Blueprint
from .auth import auth_bp
from .settings import settings_bp
from .translations import language_bp

Blueprints = [auth_bp,settings_bp,language_bp]
