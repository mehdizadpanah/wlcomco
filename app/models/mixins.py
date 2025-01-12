from datetime import datetime
from flask_login import current_user
from sqlalchemy import Column, DateTime, Integer

class TimestampMixin:
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, onupdate=datetime.utcnow, default=datetime.utcnow)

class UserTrackingMixin:
    created_by = Column(Integer, default=lambda: current_user.id if current_user else None)
    updated_by = Column(Integer, onupdate=lambda: current_user.id if current_user else None)
