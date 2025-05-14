from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import Address,NewsLetterSubscriber


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
            bio=validated_data.get('bio', '')
        )
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
    