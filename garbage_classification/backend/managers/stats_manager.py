import json
from datetime import datetime
from .base import BaseManager
from ..models import Image, DetectionHistory

class StatsManager(BaseManager):
    """Manager for system statistics and data distribution."""

    def get_data(self, **kwargs):
        return self.get_comprehensive_stats()

    def get_comprehensive_stats(self):
        from ..models import User # Inline to avoid circular if any
        total_users = User.query.count()
        today_start = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
        
        new_users_today = User.query.filter(User.created_at >= today_start).count()
        total_detections = Image.query.count()
        detections_today = Image.query.filter(Image.created_at >= today_start).count()

        # Calculate average confidence from DetectionHistory
        histories = DetectionHistory.query.filter(DetectionHistory.confidence > 0).all()
        avg_confidence = 0.0
        if histories:
            avg_confidence = sum(h.confidence for h in histories) / len(histories)
        
        # Class distribution
        class_distribution = self._get_class_distribution()

        return {
            'total_users': total_users,
            'total_detections': total_detections,
            'avg_confidence': avg_confidence,
            'daily_active': new_users_today + detections_today,
            'new_users_today': new_users_today,
            'detections_today': detections_today,
            'class_distribution': class_distribution
        }

    def _get_class_distribution(self):
        class_names = ['可回收垃圾', '有害垃圾', '厨余垃圾', '其他垃圾']
        class_counts = {name: 0 for name in class_names}
        
        all_history = DetectionHistory.query.all()
        for record in all_history:
            if record.result:
                try:
                    results = json.loads(record.result)
                    for res in results:
                        name = res.get('class_name')
                        if name == '可回收': name = '可回收垃圾'
                        elif name == '有害': name = '有害垃圾'
                        elif name == '厨余': name = '厨余垃圾'
                        elif name == '其他': name = '其他垃圾'
                        
                        if name in class_counts:
                            class_counts[name] += 1
                except:
                    continue
        return class_counts
    def get_export_data(self):
        """Compile comprehensive system data for export."""
        stats = self.get_comprehensive_stats()
        
        # Add metadata
        export_package = {
            'export_time': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'system_version': '1.0.0',
            'summary': stats,
            'status': 'verified'
        }
        return export_package
