from django.urls import path
from .views import *

app_name = 'UserApp'

urlpatterns = [
    path('login-request/', LoginRequest.as_view(), name='login request'),
    path('login-verify/', LoginVerify.as_view(), name='login verify'),
    path('register-otp-check/', RegisterOTPCheck.as_view(), name='register otp check'),
    path('register-verify/', RegisterVerify.as_view(), name='register verify'),
]