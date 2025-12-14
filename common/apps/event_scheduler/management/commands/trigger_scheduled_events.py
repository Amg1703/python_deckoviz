"""
Django management command to trigger scheduled events
Run this with: python manage.py trigger_scheduled_events
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
import requests
import os
import logging

logger = logging.getLogger(__name__)

# AI container URL
AI_CONTAINER_URL = os.getenv("AI_CONTAINER_URL", "http://deckoviz_ai:8082")


class Command(BaseCommand):
    help = 'Trigger scheduled events that are ready to execute'

    def add_arguments(self, parser):
        parser.add_argument(
            '--minutes-ahead',
            type=int,
            default=1,
            help='Generate images N minutes before scheduled time (default: 1)'
        )

    def handle(self, *args, **options):
        from apps.event_scheduler.models import Event
        
        minutes_ahead = options['minutes_ahead']
        now = timezone.now()
        trigger_time = now + timedelta(minutes=minutes_ahead)
        
        self.stdout.write(
            f"Checking for events scheduled between {now} and {trigger_time}"
        )
        
        # Find events that should be triggered
        # Events that are:
        # 1. Enabled
        # 2. Have trigger_time within the next N minutes
        # 3. Haven't been executed yet (or for recurring events, can be executed again)
        events_to_trigger = Event.objects.filter(
            enabled=True,
            trigger_time__lte=trigger_time,
            trigger_time__gt=now
        )
        
        triggered_count = 0
        failed_count = 0
        
        for event in events_to_trigger:
            try:
                self.stdout.write(f"Triggering event: {event.event_name} (ID: {event.id})")
                
                # Call AI container to generate image
                response = requests.post(
                    f"{AI_CONTAINER_URL}/event-trigger/trigger/{event.id}",
                    json={
                        "event_id": event.id,
                        "triggered_at": now.isoformat()
                    },
                    timeout=30  # Wait for initial response, actual processing happens in background
                )
                
                if response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS(f"Successfully triggered event {event.id}")
                    )
                    triggered_count += 1
                else:
                    self.stdout.write(
                        self.style.ERROR(
                            f"Failed to trigger event {event.id}: {response.status_code} - {response.text}"
                        )
                    )
                    failed_count += 1
                    
            except requests.exceptions.RequestException as e:
                self.stdout.write(
                    self.style.ERROR(f"Error triggering event {event.id}: {str(e)}")
                )
                logger.exception(f"Error triggering event {event.id}")
                failed_count += 1
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Unexpected error for event {event.id}: {str(e)}")
                )
                logger.exception(f"Unexpected error triggering event {event.id}")
                failed_count += 1
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"\nCompleted: {triggered_count} triggered, {failed_count} failed"
            )
        )
        
        if triggered_count == 0 and failed_count == 0:
            self.stdout.write("No events ready to trigger at this time")
