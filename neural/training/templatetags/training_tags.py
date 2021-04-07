"""Template tags."""

from django import template
from neural.training.models import Slot

register = template.Library()


@register.filter(name='get_icon')
def get_icon(value):
    if value in ['POWER_HOUR']:
        return 'bx bx-run text-info'
    if value in ['NEURAL_CIRCUIT']:
        return 'bx bx-dumbbell  text-danger'
    if value in ['BALANCE']:
        return 'bx bx-infinite text-warning'
    if value in ['VIRTUAL']:
        return 'bx bx-devices text-info'
    else:
        return 'bx bxs-flame  text-warning'
