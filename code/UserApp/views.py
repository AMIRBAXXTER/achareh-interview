from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import CustomUser, OTP, BlockedIPs


# Create your views here.


class LoginRequest(APIView):
    def post(self, request):

        user = CustomUser.objects.filter(phone_number=request.data.get('phone_number')).first()
        if user and not user.is_active:
            return Response({'message': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)

        is_blocked = BlockedIPs.objects.filter(ip=request.META.get('REMOTE_ADDR')).exists()
        if is_blocked:
            return Response({'message': 'IP is blocked'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            user = CustomUser.objects.filter(phone_number=serializer.data.get('phone_number')).first()
            if user:
                return Response({'message': 'User exists and can login'}, status=status.HTTP_200_OK)
            new_otp = OTP.objects.create(phone_number=serializer.validated_data.get('phone_number'))
            return Response({'your OTP': new_otp.otp}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class LoginVerify(APIView):
    def post(self, request):
        phone_number = request.data.get('phone_number')
        user = CustomUser.objects.filter(phone_number=phone_number).first()
        if user and not user.is_active:
            return Response({'message': 'User is blocked'}, status=status.HTTP_403_FORBIDDEN)

        is_blocked = BlockedIPs.objects.filter(ip=request.META.get('REMOTE_ADDR')).exists()
        if is_blocked:
            return Response({'message': 'IP is blocked'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = LoginVerifySerializer(data=request.data)
        if serializer.is_valid():
            sv = serializer.validated_data
            user = authenticate(request, username=sv['phone_number'], password=sv['password'])

            if not user:
                return Response({'error': 'Phone number or password is wrong'}, status=status.HTTP_404_NOT_FOUND)

            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterOTPCheck(APIView):
    def post(self, request):

        is_blocked = BlockedIPs.objects.filter(ip=request.META.get('REMOTE_ADDR')).exists()
        if is_blocked:
            return Response({'message': 'IP is blocked'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterOTPCheckSerializer(data=request.data)
        if serializer.is_valid():
            otp = OTP.objects.filter(phone_number=serializer.data.get('phone_number')).first()
            if otp:
                if otp.otp == serializer.data.get('code') and otp.is_valid:
                    otp.delete()
                    return Response({'message': 'OTP verified'}, status=status.HTTP_200_OK)

                return Response({'message': 'OTP is not correct'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'massage': 'no OTP exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterVerify(APIView):
    def post(self, request):

        is_blocked = BlockedIPs.objects.filter(ip=request.META.get('REMOTE_ADDR')).exists()
        if is_blocked:
            return Response({'message': 'IP is blocked'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = RegisterVerifySerializer(data=request.data)
        if serializer.is_valid():
            sv = serializer.validated_data
            user = CustomUser.objects.create(
                phone_number=sv['phone_number'],
                first_name=sv['first_name'],
                last_name=sv['last_name'],
            )
            password = sv['password']
            user.set_password(password)
            user.save()
            return Response({'message': 'User created', 'user': serializer.data}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
