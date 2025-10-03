from django.db import migrations, models
import django.db.models.deletion

def migrate_to_asset_model(apps, schema_editor):
    # Get the current state of the models
    Blog = apps.get_model('blogs', 'Blog')
    Asset = apps.get_model('blogs', 'Asset')
    Image = apps.get_model('gallery', 'Image')
    
    # Create a mapping of old image IDs to new asset IDs
    image_to_asset = {}
    
    # Process images
    for blog in Blog.objects.all():
        # Handle images
        for image in blog.images.all():
            if image.id not in image_to_asset:
                # Create a new Asset for this Image
                asset = Asset.objects.create(file=image.file)
                image_to_asset[image.id] = asset.id
            # Add the new relationship
            blog.images_new.add(image_to_asset[image.id])
        
        # Handle videos
        for video in blog.videos.all():
            if video.id not in image_to_asset:
                # Create a new Asset for this Video
                asset = Asset.objects.create(file=video.file)
                image_to_asset[video.id] = asset.id
            # Add the new relationship
            blog.videos_new.add(image_to_asset[video.id])

class Migration(migrations.Migration):
    dependencies = [
        ('blogs', '0001_initial'),
    ]

    operations = [
        # Create the new Asset model
        migrations.CreateModel(
            name='Asset',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('file', models.FileField(upload_to='assets')),
            ],
        ),
        
        # Add the new many-to-many fields
        migrations.AddField(
            model_name='blog',
            name='images_new',
            field=models.ManyToManyField(blank=True, related_name='blogs_images', to='blogs.asset'),
        ),
        migrations.AddField(
            model_name='blog',
            name='videos_new',
            field=models.ManyToManyField(blank=True, related_name='blogs_videos', to='blogs.asset'),
        ),
        
        # Run the data migration
        migrations.RunPython(migrate_to_asset_model),
        
        # Remove the old fields
        migrations.RemoveField(
            model_name='blog',
            name='images',
        ),
        migrations.RemoveField(
            model_name='blog',
            name='videos',
        ),
        
        # Rename the new fields to match the model
        migrations.RenameField(
            model_name='blog',
            old_name='images_new',
            new_name='images',
        ),
        migrations.RenameField(
            model_name='blog',
            old_name='videos_new',
            new_name='videos',
        ),
    ]