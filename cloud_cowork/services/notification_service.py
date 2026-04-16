"""Notification Service for Cloud Cowork HUD"""

from datetime import datetime
from typing import List, Dict

class NotificationService:
    """Notification service for managing system notifications"""
    
    def __init__(self):
        self.notifications = []
        self.max_notifications = 20
    
    def add_notification(self, title: str, message: str, notification_type: str = "info"):
        """Add a new notification"""
        notification = {
            "id": len(self.notifications) + 1,
            "title": title,
            "message": message,
            "type": notification_type,
            "timestamp": datetime.now().isoformat(),
            "read": False
        }
        
        self.notifications.insert(0, notification)
        
        # Keep only recent notifications
        if len(self.notifications) > self.max_notifications:
            self.notifications = self.notifications[:self.max_notifications]
    
    def mark_read(self, notification_id: int):
        """Mark notification as read"""
        for notification in self.notifications:
            if notification["id"] == notification_id:
                notification["read"] = True
                break
    
    def get_recent_notifications(self) -> List[Dict]:
        """Get recent notifications"""
        return self.notifications
    
    def clear_notifications(self):
        """Clear all notifications"""
        self.notifications = []
    
    def get_unread_count(self) -> int:
        """Get count of unread notifications"""
        return sum(1 for n in self.notifications if not n["read"])
