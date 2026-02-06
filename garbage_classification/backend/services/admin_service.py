from ..managers import StatsManager, UserManager, LogsManager

class AdminService:
    def __init__(self):
        self.stats_manager = StatsManager()
        self.user_manager = UserManager()
        self.logs_manager = LogsManager()

    def get_dashboard_stats(self):
        return self.stats_manager.get_data()

    def get_users_list(self):
        return self.user_manager.get_data()

    def get_system_logs(self, page=1, per_page=20):
        return self.logs_manager.get_data(page=page, per_page=per_page)

    def export_system_data(self):
        return self.stats_manager.get_export_data()

admin_service = AdminService()
