from rest_framework import serializers
from django.contrib.auth import get_user_model

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
            'created_at',
            'updated_at',
        ]
        read_only_fields = [
            'id', 
            'username',
            'email',
            'created_at',
            'updated_at', 
        ]
