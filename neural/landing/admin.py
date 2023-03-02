# Django
from django.contrib import admin

# Models
from neural.landing.models import HeaderLanding, MainContentHeader, ServicesLanding, PersonalTrainer



@admin.register(ServicesLanding)
class ServicesLandingAdmin(admin.ModelAdmin):
    list_display = ["title",]


@admin.register(HeaderLanding)
class HeaderLandingAdmin(admin.ModelAdmin):
    pass


@admin.register(MainContentHeader)
class MainContentHeaderAdmin(admin.ModelAdmin):
    pass

@admin.register(PersonalTrainer)
class PersonalTrainerAdmin(admin.ModelAdmin):
    list_display = ["name",]