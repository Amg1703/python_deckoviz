import os
import json
from django.core.management.base import BaseCommand
from django.db import transaction
from apps.credits.models import CreditPackage
from django.utils import timezone
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Load initial credit packages from fixture file'

    def handle(self, *args, **options):
        fixture_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.dirname(__file__))),
            'fixtures',
            'initial_plans.json'
        )
        
        if not os.path.exists(fixture_path):
            self.stdout.write(self.style.ERROR(f'Fixture file not found: {fixture_path}'))
            return
        
        try:
            with open(fixture_path, 'r') as f:
                plans_data = json.load(f)
            
            with transaction.atomic():
                created_count = 0
                updated_count = 0
                
                for plan_data in plans_data:
                    if plan_data['model'] != 'credits.creditpackage':
                        continue
                    
                    fields = plan_data['fields']
                    plan_id = fields.pop('id', None)
                    
                    # Handle created_at and updated_at fields
                    if 'created_at' in fields:
                        fields['created_at'] = timezone.datetime.fromisoformat(fields['created_at'].replace('Z', '+00:00'))
                    if 'updated_at' in fields:
                        fields['updated_at'] = timezone.datetime.fromisoformat(fields['updated_at'].replace('Z', '+00:00'))
                    
                    # Try to get existing package or create a new one
                    if plan_id:
                        package, created = CreditPackage.objects.update_or_create(
                            id=plan_id,
                            defaults=fields
                        )
                    else:
                        package, created = CreditPackage.objects.get_or_create(
                            name=fields['name'],
                            defaults=fields
                        )
                    
                    if created:
                        created_count += 1
                    else:
                        updated_count += 1
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully loaded credit packages: {created_count} created, {updated_count} updated'
                    )
                )
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error loading credit packages: {str(e)}'))
            logger.exception("Error loading credit packages")
