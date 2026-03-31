from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OTP

User = get_user_model()

class SendOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

    def validate_phone_number(self, value):
        if not User.objects.filter(phone_number=value).exists():
            raise serializers.ValidationError("User with this phone number does not exist.")
        return value

class VerifyOTPSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)

class AdminVerifyUserSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    is_verified = serializers.BooleanField(default=True)
