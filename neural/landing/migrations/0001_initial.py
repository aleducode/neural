# Generated by Django 3.2.16 on 2023-01-25 03:47

import ckeditor.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='HeaderLanding',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('header_title', ckeditor.fields.RichTextField()),
                ('header_description', ckeditor.fields.RichTextField()),
                ('header_image', models.ImageField(upload_to='header_images')),
            ],
            options={
                'verbose_name': 'Header section',
                'verbose_name_plural': 'Header section',
            },
        ),
        migrations.CreateModel(
            name='MainContentHeader',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True, help_text='Date time on which the object was created.', verbose_name='created at')),
                ('modified', models.DateTimeField(auto_now=True, help_text='Date time on which the object was last modified.', verbose_name='modified at')),
                ('description', ckeditor.fields.RichTextField()),
                ('video_services', models.FileField(upload_to='landing_videos')),
                ('video_trainng', models.FileField(upload_to='landing_videos')),
                ('description_services', ckeditor.fields.RichTextField()),
                ('description_training', ckeditor.fields.RichTextField()),
            ],
            options={
                'verbose_name': 'Main content section',
                'verbose_name_plural': 'Main content section',
            },
        ),
    ]
