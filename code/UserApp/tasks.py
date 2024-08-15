from config.celery_base import app
from .models import CustomUser, BlockedIPs


@app.task(queue='tasks')
def unblock_user(user_id):
    user = CustomUser.objects.filter(id=user_id).first()
    user.is_active = True
    user.save()


@app.task(queue='tasks')
def unblock_ip(ip):
    blocked_ip = BlockedIPs.objects.filter(ip=ip).first()
    if blocked_ip:
        blocked_ip.delete()
