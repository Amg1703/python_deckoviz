import os

def user_directory_path(instance, filename):
    user_id = instance.uploaded_by.id if instance.uploaded_by else 'anonymous'
    return os.path.join('images', str(user_id), filename)
