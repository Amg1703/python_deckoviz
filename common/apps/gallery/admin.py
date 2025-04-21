from django.contrib import admin
from .models import Image, Collection,CollectionImage

admin.site.register(Image)
admin.site.register(Collection)
admin.site.register(CollectionImage)