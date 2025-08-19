from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'date_joined')
        read_only_fields = ('id', 'username', 'date_joined')

class UserUpdateSerializer(serializers.ModelSerializer):
    current_password = serializers.CharField(write_only=True, required=False)
    new_password = serializers.CharField(write_only=True, required=False)
    confirm_password = serializers.CharField(write_only=True, required=False)

    class Meta:
        model = User
        fields = ('email', 'first_name', 'last_name', 'current_password', 'new_password', 'confirm_password')

    def validate(self, data):
        if 'new_password' in data:
            if 'current_password' not in data:
                raise serializers.ValidationError("Current password is required to set new password")
            if data['new_password'] != data.get('confirm_password', ''):
                raise serializers.ValidationError("New passwords don't match")
        return data

    def update(self, instance, validated_data):
        # Check current password if changing password
        current_password = validated_data.pop('current_password', None)
        new_password = validated_data.pop('new_password', None)
        validated_data.pop('confirm_password', None)

        if new_password and current_password:
            if not instance.check_password(current_password):
                raise serializers.ValidationError({"current_password": "Current password is incorrect"})
            instance.set_password(new_password)

        return super().update(instance, validated_data)