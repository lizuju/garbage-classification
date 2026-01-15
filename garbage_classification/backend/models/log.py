from datetime import datetime

from ..extensions import db


class SystemLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    log_type = db.Column(db.String(20), nullable=False)  # 'info', 'error', 'user_action'
    message = db.Column(db.Text, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    user = db.relationship('User', backref=db.backref('logs', lazy=True))

