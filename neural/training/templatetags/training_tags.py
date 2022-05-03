"""Template tags."""

from django import template

register = template.Library()


@register.filter(name='get_icon')
def get_icon(value):
    if value in ['FUNCIONAL_TRAINING']:
        return 'bx bx-dumbbell  text-danger'
    if value in ['GAP_MMSS']:
        return 'mdi mdi-transit-transfer text-dark'
    if value in ['CARDIO_STEP']:
        return 'bx bx-run text-info'
    if value in ['SENIOR']:
        return 'mdi mdi-biathlon text-success'
    if value in ['RTG']:
        return 'mdi mdi-dolly text-dark'
    if value in ['PILATES']:
        return 'mdi mdi-karate text-info'
    if value in ['FIT_BOXING']:
        return 'mdi mdi-boxing-glove text-warning'
    if value in ['BALANCE']:
        return 'mdi mdi-nature-people text-warning'
    if value in ['SUPERSTAR']:
        return 'bx bx-star text-warning'
    if value in ['CARDIOHIT']:
        return 'mdi mdi-run-fast text-info'
    if value in ['A_FUEGO']:
        return 'bx bxs-flame  text-warning'
    if value in ['RUMBA']:
        return 'mdi mdi-music-circle-outline text-info'
    else:
        return 'bx bxs-flame  text-warning'
