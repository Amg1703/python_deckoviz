import os
import posixpath

def _get_user_id(instance):
    if hasattr(instance, 'uploaded_by') and instance.uploaded_by:
        user = instance.uploaded_by
    elif hasattr(instance, 'user') and instance.user:
        user = instance.user
    else:
        user = None
    return str(user.id) if user and getattr(user, 'id', None) else 'anonymous'

def user_image_path(instance, filename):
    user_id = _get_user_id(instance)
    return posixpath.join('images', user_id, filename)

def user_music_path(instance, filename):
    user_id = _get_user_id(instance)
    return posixpath.join('music', user_id, filename)

def user_audio_path(instance, filename):
    user_id = _get_user_id(instance)
    return posixpath.join('audios', user_id, filename)

def user_video_path(instance, filename):
    user_id = _get_user_id(instance)
    return posixpath.join('videos', user_id, filename)

def user_transcript_path(instance, filename):
    user_id = _get_user_id(instance)
    return posixpath.join('transcripts', user_id, filename)