from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import CollectionImage
from .collection_meta_generator import aggregate_collection_metadata

@receiver([post_save, post_delete], sender=CollectionImage)
def update_collection_metadata(sender, instance, **kwargs):
    collection = instance.collection
    # Fetch all image metadata dicts
    image_metadatas = list(collection.collection_images.select_related('image').values_list('image__metadata', flat=True))
    # Aggregate metadata locally
    metadata = aggregate_collection_metadata(image_metadatas)
    collection.metadata = metadata
    collection.save(update_fields=['metadata']) 