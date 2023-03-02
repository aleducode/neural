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

    def __str__(self):
        return "Título landing"

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


class ServicesLanding(NeuralBaseModel):
    """List services landing page."""

    title = models.CharField(max_length=500)
    service_image = models.ImageField(upload_to='header_images')
    service_description = RichTextField()
    main_content = models.ForeignKey(MainContentHeader, on_delete=models.CASCADE, related_name="services")

    def __str__(self):
        return f"Servicio {self.title}"

    class Meta:
        verbose_name = 'service'
        verbose_name_plural = 'Services'


class PersonalTrainer(NeuralBaseModel):
    """Personal training model."""

    name = models.CharField(max_length=200)
    description = RichTextField()
    image = models.ImageField(upload_to='personal_trainer')
    url_facebook = models.CharField(max_length=200)
    url_ig = models.CharField(max_length=200)

    def __str__(self):
        return f"Entrenador {self.name}"

    class Meta:
        verbose_name = 'Entrenador'
        verbose_name_plural = 'Entrenadores'
