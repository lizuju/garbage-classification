from ..extensions import db
from ..models import SystemLog


def log_action(log_type, message, user_id=None):
    """记录系统日志，使用独立的session避免影响主事务"""
    try:
        log = SystemLog(log_type=log_type, message=message, user_id=user_id)
        db.session.add(log)
        db.session.commit()
    except Exception as e:
        # 日志失败不应该中断主程序
        db.session.rollback()
        print(f"日志记录异常: {log_type} - {message} - {e}")

