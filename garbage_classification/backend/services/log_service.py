from ..extensions import db
from ..models import SystemLog


def log_action(log_type, message, user_id=None):
    log = SystemLog(log_type=log_type, message=message, user_id=user_id)
    db.session.add(log)
    db.session.commit()

