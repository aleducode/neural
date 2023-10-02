"""Template tags."""

from django import template

register = template.Library()


@register.filter(name='get_icon')
def get_icon(value):
    if value.slug_name in ['funcional-training']:
        return 'bx bx-dumbbell  text-danger'
    if value.slug_name in ['gap']:
        return 'mdi mdi-transit-transfer text-dark'
    if value.slug_name in ['aeroibic-step']:
        return 'bx bx-run text-info'
    if value.slug_name in ['senior']:
        return 'mdi mdi-biathlon text-success'
    if value.slug_name in ['rtg']:
        return 'mdi mdi-dolly text-dark'
    if value.slug_name in ['pilates']:
        return 'mdi mdi-karate text-info'
    if value.slug_name in ['funcional-box']:
        return 'mdi mdi-boxing-glove text-warning'
    if value.slug_name in ['balance']:
        return 'mdi mdi-nature-people text-warning'
    if value.slug_name in ['super-star']:
        return 'bx bx-star text-warning'
    if value.slug_name in ['cardio-hit']:
        return 'mdi mdi-run-fast text-info'
    if value.slug_name in ['a-fuego']:
        return 'bx bxs-flame  text-warning'
    if value.slug_name in ['rumba']:
        return 'mdi mdi-music-circle-outline text-info'
    else:
        return 'bx bxs-flame  text-warning'
