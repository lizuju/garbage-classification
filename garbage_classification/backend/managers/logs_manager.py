from .base import BaseManager
from ..models import SystemLog, User

class LogsManager(BaseManager):
    """Manager for system logs."""

    def get_data(self, **kwargs):
        page = kwargs.get('page', 1)
        per_page = kwargs.get('per_page', 20)
        
        pagination = SystemLog.query.order_by(SystemLog.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        logs = []
        for log in pagination.items:
            log_dict = {
                'id': log.id,
                'log_type': log.log_type,
                'message': log.message,
                'user_id': log.user_id,
                'created_at': log.created_at.isoformat()
            }
            if log.user_id:
                user = User.query.get(log.user_id)
                if user:
                    log_dict['username'] = user.username
            logs.append(log_dict)
            
        return {
            'items': logs,
            'total': pagination.total,
            'pages': pagination.pages,
            'current_page': page
        }
