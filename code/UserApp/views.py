from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import *
from .models import CustomUser, OTP, BlockedIPs


# Create your views here.


class LoginRequest(APIView):
    def post(self, request):

        response = check_block_status(request)
        if response:
            return response

        serializer = LoginRequestSerializer(data=request.data)
        if serializer.is_valid():
            sv = serializer.validated_data
            user = CustomUser.get_or_none(phone_number=sv['phone_number'])
            if user:
                return Response({'message': 'User exists and can login'}, status=status.HTTP_200_OK)
            new_otp = OTP.objects.create(phone_number=sv['phone_number'])
            send_sms(phone_number=new_otp.phone_number, message='Your OTP is: ' + new_otp.otp)
            return Response({'message': 'otp sent to user'}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginVerify(APIView):
    def post(self, request):

        response = check_block_status(request)
        if response:
            return response

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

        response = check_block_status(request, is_registered=False)
        if response:
            return response

        serializer = RegisterOTPCheckSerializer(data=request.data)
        if serializer.is_valid():
            sv = serializer.validated_data
            otp = OTP.get_or_none(phone_number=sv['phone_number'])
            if otp:
                if otp.otp == sv['code'] and otp.is_valid:
                    otp.delete()
                    return Response({'message': 'OTP verified'}, status=status.HTTP_200_OK)

                return Response({'message': 'OTP is not correct'}, status=status.HTTP_400_BAD_REQUEST)
            return Response({'massage': 'no OTP exists'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterVerify(APIView):
    def post(self, request):

        response = check_block_status(request, is_registered=False)
        if response:
            return response

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
