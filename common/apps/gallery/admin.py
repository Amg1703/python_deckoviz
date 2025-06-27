from django.contrib import admin
from .models import Image, Collection,CollectionImage,Audio, DailyCuration

admin.site.register(Image)
admin.site.register(Collection)
admin.site.register(CollectionImage)
admin.site.register(Audio)

@admin.register(DailyCuration)
class DailyCurationAdmin(admin.ModelAdmin):
    list_display = ('date',)
    filter_horizontal = ('collections',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == 'collections':
            kwargs["queryset"] = Collection.objects.filter(view='public', is_active=True)
        return super().formfield_for_manytomany(db_field, request, **kwargs)