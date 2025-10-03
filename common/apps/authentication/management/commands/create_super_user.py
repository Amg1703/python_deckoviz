from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Create a superuser with specified environment variables'

    def handle(self, *args, **kwargs):
        Tenant = get_user_model()
        username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not username:
            self.stdout.write(self.style.ERROR('DJANGO_SUPERUSER_USERNAME environment variable is not set.'))
            return

        if not email:
            self.stdout.write(self.style.ERROR('DJANGO_SUPERUSER_EMAIL environment variable is not set.'))
            return

        if not password:
            self.stdout.write(self.style.ERROR('DJANGO_SUPERUSER_PASSWORD environment variable is not set.'))
            return

        if not Tenant.objects.filter(username=email).exists():
            Tenant.objects.create_superuser(username=email, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{email}" created successfully'))
        else:
            self.stdout.write(self.style.WARNING(f'Superuser "{email}" already exists'))
