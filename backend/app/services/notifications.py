from app.models.entities import Notification


def enqueue_notification(user_id: int, message: str, channel: str = "email") -> Notification:
    return Notification(user_id=user_id, message=message, channel=channel)
