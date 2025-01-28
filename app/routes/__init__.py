from flask import Blueprint
from .auth import auth_bp
from .settings import settings_bp

Blueprints = [auth_bp,settings_bp]
