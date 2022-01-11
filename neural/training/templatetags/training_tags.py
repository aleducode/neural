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
    if value in ['TRX']:
        return 'mdi mdi-odnoklassniki text-info'
    if value in ['YOGA']:
        return 'mdi mdi-yoga text-info'
    if value in ['TONO']:
        return 'bx bx-cycling text-info'
    if value in ['BODY_PUMP']:
        return 'mdi mdi-airbag text-warning'
    if value in ['RUMBA']:
        return 'mdi mdi-music-circle-outline text-info'
    else:
        return 'bx bxs-flame  text-warning'
