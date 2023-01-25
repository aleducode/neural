# Django
from django.db import models

# Utils
from ckeditor.fields import RichTextField
from neural.utils.models import NeuralBaseModel

# Create your models here.
class HeaderLanding(NeuralBaseModel):
    """Header section landing."""

    header_title = RichTextField()
    header_description = RichTextField()
    header_image = models.ImageField(upload_to='header_images')

    class Meta:
        verbose_name = 'Header section'
        verbose_name_plural = 'Header section'
    
class MainContentHeader(NeuralBaseModel):
    """Main content section."""

    description = RichTextField()
    video_services = models.FileField(upload_to='landing_videos')
    video_trainng = models.FileField(upload_to='landing_videos')
    description_services = RichTextField()
    description_training = RichTextField()

    class Meta:
        verbose_name = 'Main content section'
        verbose_name_plural = 'Main content section'