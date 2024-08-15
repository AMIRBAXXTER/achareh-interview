from datetime import timedelta
from django.utils import timezone
from django.contrib.auth import authenticate
from rest_framework import status
from rest_framework.response import Response

from .models import CustomUser, FailedLoginTry, OTP, BlockedIPs
from .tasks import unblock_user, unblock_ip


class FailedLoginMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path == '/login-verify/':
            phone_number = request.POST.get('phone_number')
            password = request.POST.get('password')
            user = authenticate(request, phone_number=phone_number, password=password)
            if user is None:
                user = CustomUser.objects.filter(phone_number=phone_number).first()
                ip = request.META.get('REMOTE_ADDR')
                if user:

                    FailedLoginTry.objects.create(user=user, ip=ip)
                    all_tries_count_by_user = FailedLoginTry.objects.filter(user=user)
                    all_tries_count_by_ip = FailedLoginTry.objects.filter(ip=ip)

                    if all_tries_count_by_user.filter(timestamp__gte=timezone.now() - timedelta(
                            minutes=5)).count() >= 4 or all_tries_count_by_ip.filter(
                        timestamp__gte=timezone.now() - timedelta(
                            minutes=5)).count() >= 4:
                        user.is_active = False
                        user.save()
                        all_tries_count_by_user.delete()
                        all_tries_count_by_ip.delete()
                        unblock_user.apply_async(args=[user.id], countdown=60)
                else:
                    FailedLoginTry.objects.create(ip=ip)
                    all_tries_count_by_ip = FailedLoginTry.objects.filter(ip=ip)
                    if all_tries_count_by_ip.filter(timestamp__gte=timezone.now() - timedelta(
                            minutes=5)).count() >= 4:
                        BlockedIPs.objects.create(ip=ip)
                        all_tries_count_by_ip.delete()
                        unblock_ip.apply_async(args=[ip], countdown=60)

        response = self.get_response(request)

        return response


class FailedRegisterMiddleware:

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and request.path == '/register-otp-check/':
            phone_number = request.POST.get('phone_number')
            ip = request.META.get('REMOTE_ADDR')
            otp = request.POST.get('code')
            is_blocked = BlockedIPs.objects.filter(ip=ip).exists()
            if not is_blocked:
                registered_otp = OTP.objects.filter(phone_number=phone_number).first()
                if registered_otp is not None:
                    if registered_otp.otp != otp:

                        FailedLoginTry.objects.create(user=None, ip=ip)
                        all_tries_count_by_ip = FailedLoginTry.objects.filter(ip=ip)
                        if all_tries_count_by_ip.filter(timestamp__gte=timezone.now() - timedelta(
                                minutes=5)).count() >= 4:
                            BlockedIPs.objects.create(ip=ip)
                            all_tries_count_by_ip.delete()
                            registered_otp.delete()
                            unblock_ip.apply_async(args=[ip], countdown=60)

        response = self.get_response(request)

        return response
