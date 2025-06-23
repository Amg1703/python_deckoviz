from rest_framework import serializers
from .models import Mode, UserMode, Session, Music
from apps.gallery.models import Collection
from apps.gallery.serializers import CollectionSerializer

class MusicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Music
        fields = '__all__'

class ModeSerializer(serializers.ModelSerializer):
    admin_collections = CollectionSerializer(many=True, read_only=True)
    admin_curations = CollectionSerializer(many=True, read_only=True)
    admin_music = MusicSerializer(many=True, read_only=True)

    class Meta:
        model = Mode
        fields = ('id', 'name', 'admin_collections', 'admin_curations', 'admin_music')

class UserModeSerializer(serializers.ModelSerializer):
    user_collections = CollectionSerializer(many=True, read_only=True)
    user_music = MusicSerializer(many=True, read_only=True)
    mode = ModeSerializer(read_only=True)

    class Meta:
        model = UserMode
        fields = ('id', 'user', 'mode', 'user_collections', 'user_music')

class UserModeUpdateSerializer(serializers.ModelSerializer):
    user_collections = serializers.PrimaryKeyRelatedField(
        queryset=Collection.objects.all(),
        many=True,
        required=False
    )
    user_music = serializers.PrimaryKeyRelatedField(
        queryset=Music.objects.all(),
        many=True,
        required=False
    )

    class Meta:
        model = UserMode
        fields = ('user_collections', 'user_music')

class SessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Session
        fields = '__all__'
