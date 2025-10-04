from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('gallery', '0006_dailycuration'),
    ]

    operations = [
        migrations.AddField(
            model_name='collection',
            name='music_title',
            field=models.CharField(max_length=255, blank=True, null=True, help_text="Optional title for the collection's music"),
        ),
    ] 