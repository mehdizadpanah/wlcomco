from datetime import datetime
from ..extensions import db
from .mixins import TimestampMixin, UserTrackingMixin

class Notification(db.Model, TimestampMixin, UserTrackingMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    send_via = db.Column(db.Enum('email', 'sms'), nullable=False)
    content_type = db.Column(db.Enum('text', 'html'), nullable=False)
    description = db.Column(db.Text)
    subject = db.Column(db.String(255))
    body = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"<Notification {self.name}>"

    @staticmethod
    def get_notifications():
        notifications = Notification.query.all()
        return notifications
