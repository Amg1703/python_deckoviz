from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address,NewsLetterSubscriber, UserProfile
from django.contrib.auth.password_validation import validate_password
from .models import PasswordResetToken
from django.utils.translation import gettext_lazy as _


User = get_user_model() 


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'profile_visible', 'bio']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            profile_visible=validated_data.get('profile_visible', True),
            bio=validated_data.get('bio', ''),
        )
        user.is_active = False
        user.email_verified = False
        user.save()
        return user

 
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'id', 
            'username',
            'email',
            'first_name',
            'last_name',
            'profile_visible',
            'profile_picture',
            'banner_pictures',
            'bio',
            'is_active',
            'room',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 
            'username',
            'email',
            'room',
            'created_at',
            'updated_at', 
        ]


class AddressSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Address
        fields = [
            'id',
            'address_type',
            'address',
            'city',
            'state',
            'country',
            'zip_code',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]
    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class NewsLetterSubscriberSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsLetterSubscriber
        fields = [
            'id',
            'email',
            'name',
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
        ]


class UserProfileSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField(read_only=True)
    email = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = UserProfile
        fields = [
            'name', 'email',
            'age', 'gender', 'location', 'vocation', 'hobbies', 'passions', 'interests',
            'desired_states', 'personal_beliefs', 'life_principles', 'core_values',
            'secondary_values', 'hopes_and_dreams'
        ]

    def get_name(self, obj):
        # Combine first and last name, fallback to username
        if obj.user.first_name or obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}".strip()
        return obj.user.username

    def get_email(self, obj):
        return obj.user.email

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 


class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate_password(self, value):
        validate_password(value)
        return value 


class EmailVerificationSerializer(serializers.Serializer):
    token = serializers.CharField() 


class ResendVerificationSerializer(serializers.Serializer):
    email = serializers.EmailField() 