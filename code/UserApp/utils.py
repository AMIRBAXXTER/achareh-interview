from rest_framework import serializers, status
from rest_framework.response import Response

from .models import CustomUser, BlockedIPs


def check_phone(phone_number, self=None):
    message = []
    if len(phone_number) != 11:
        message.append('phone number must be 11 digit')
    if not phone_number.startswith('09'):
        message.append('phone number must start with 09')
    if not phone_number.isdigit():
        message.append('phone number must include only digits')
    if message:
        raise serializers.ValidationError(message)
    return phone_number


def check_block_status(request, is_registered=True):
    if is_registered:
        user = CustomUser.get_or_none(phone_number=request.data.get('phone_number'))
        if user and not user.is_active:
            return Response({'message': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)

    is_blocked = BlockedIPs.get_or_none(ip=request.META.get('REMOTE_ADDR'))
    if is_blocked:
        return Response({'message': 'IP is blocked'}, status=status.HTTP_400_BAD_REQUEST)


def send_sms(phone_number, message):
    print(f'message: ({message}) sent to {phone_number}')