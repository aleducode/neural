# Django
from django.contrib import admin

# Models
from neural.landing.models import HeaderLanding, MainContentHeader, ServicesLanding


class ServicesInline(admin.StackedInline):
    model = ServicesLanding
    extra = 0


@admin.register(HeaderLanding)
class HeaderLandingAdmin(admin.ModelAdmin):
    pass


@admin.register(MainContentHeader)
class MainContentHeaderAdmin(admin.ModelAdmin):
    inlines = [ServicesInline]