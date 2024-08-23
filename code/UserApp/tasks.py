from config.celery_base import app
from .models import CustomUser, BlockedIPs


@app.task(queue='tasks')
def unblock_user(user_id):
    user = CustomUser.get_or_none(id=user_id)
    user.is_active = True
    user.save()


@app.task(queue='tasks')
def unblock_ip(ip):
    blocked_ip = BlockedIPs.get_or_none(ip=ip)
    if blocked_ip:
        blocked_ip.delete()
