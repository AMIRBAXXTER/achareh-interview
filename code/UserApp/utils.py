from rest_framework import serializers, status
from rest_framework.response import Response

from .models import CustomUser, BlockedIPs


# def check_phone(phone_number, self=None):
#     if len(phone_number) != 11:
#         raise serializers.ValidationError('phone number must be 11 digit')
#     if not phone_number.startswith('09'):
#         raise serializers.ValidationError('phone number must start with 09')
#     if not phone_number.isdigit():
#         raise serializers.ValidationError('phone number must include only digits')
#
#     return phone_number
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
        user = CustomUser.objects.filter(phone_number=request.data.get('phone_number')).first()
        if user:
            if not user.is_active:
                return Response({'massage: ': 'User is blocked'})
    is_blocked = BlockedIPs.objects.filter(ip=request.META.get('REMOTE_ADDR')).exists()
    if is_blocked:
        return Response({'massage': 'IP is blocked'}, status=status.HTTP_400_BAD_REQUEST)

