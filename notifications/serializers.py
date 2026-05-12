from rest_framework import serializers
from .models import Notification

class NotificationSerializer(serializers.ModelSerializer):
    status_text = serializers.SerializerMethodField()

    class Meta:
        model = Notification
        fields = ['id', 'user', 'title', 'message', 'notification_type', 'is_read', 'status_text', 'created_at']
        read_only_fields = ['user', 'created_at']

    def get_status_text(self, obj):
        return "Хонда шудааст" if obj.is_read else "Хонда нашудааст"