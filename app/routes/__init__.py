from flask import Blueprint
from .auth import auth_bp
from .general_settings import general_settings_bp

Blueprints = [auth_bp,general_settings_bp]
