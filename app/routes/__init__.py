from flask import Blueprint
from .auth import auth_bp

Blueprints = [auth_bp]
