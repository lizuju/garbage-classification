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
        total_detections = DetectionHistory.query.count()
        detections_today = DetectionHistory.query.filter(DetectionHistory.created_at >= today_start).count()

        # Calculate average confidence from top-1 per record (use result JSON if available)
        histories = DetectionHistory.query.all()
        avg_confidence = 0.0
        top_confidences = []
        for record in histories:
            if not record.result:
                continue
            try:
                results = json.loads(record.result)
                if not results:
                    continue
                top_item = max(results, key=lambda r: r.get('confidence', 0))
                conf = float(top_item.get('confidence', 0))
                if conf > 0:
                    top_confidences.append(conf)
            except Exception:
                continue
        if top_confidences:
            avg_confidence = sum(top_confidences) / len(top_confidences)
        
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
        class_names = ['可回收物', '有害垃圾', '厨余垃圾', '其他垃圾']
        class_counts = {name: 0 for name in class_names}
        
        all_history = DetectionHistory.query.all()
        for record in all_history:
            if record.result:
                try:
                    results = json.loads(record.result)
                    if not results:
                        continue
                    top_item = max(results, key=lambda r: r.get('confidence', 0))
                    name = top_item.get('class_name', '')
                    if '可回收' in name:
                        name = '可回收物'
                    elif '有害' in name:
                        name = '有害垃圾'
                    elif '厨余' in name:
                        name = '厨余垃圾'
                    else:
                        name = '其他垃圾'

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
