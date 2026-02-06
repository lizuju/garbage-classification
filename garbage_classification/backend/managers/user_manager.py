from .base import BaseManager
from ..models import User

class UserManager(BaseManager):
    """Manager for user administration."""

    def get_data(self, **kwargs):
        users = User.query.all()
        return [user.to_dict() for user in users]
