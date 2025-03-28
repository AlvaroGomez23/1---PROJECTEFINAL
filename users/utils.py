from .models import Notification

def send_user_notification(user, user_from, title, message, exchange):
    Notification.objects.create(user=user, user_from=user_from, title=title, message=message, exchange=exchange)