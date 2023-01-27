# Django
from django.contrib import admin

# Models
from neural.landing.models import HeaderLanding, MainContentHeader


@admin.register(HeaderLanding)
class HeaderLandingAdmin(admin.ModelAdmin):
    pass


@admin.register(MainContentHeader)
class MainContentHeaderAdmin(admin.ModelAdmin):
    pass