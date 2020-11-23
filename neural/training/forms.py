"""Training forms."""

from django import forms
from django.utils import timezone
from datetime import timedelta
from neural.training.models import UserTraining, Slot


days_wrapper = ['Hoy', 'Mañana', 'Pasado Mañana']


class SchduleForm(forms.Form):
    """Schedule form."""

    def __init__(self, request=None, *args, **kwargs):
        SLOT_CHOICES = [('', 'Seleccionar')]
        if 'user' in kwargs:
            self.user = kwargs.pop('user')

        # Constructor slots
        if 'slots' in kwargs:
            self.slots = kwargs.pop('slots')
            for slot in self.slots:
                initial = slot.get('hour_init')
                end = slot.get('hour_end')
                schedule = f'{initial} a {end}'
                SLOT_CHOICES += [(slot.get('id'), schedule)]

        super().__init__(*args, **kwargs)
        self.fields['slot'].widget = forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
        self.fields['slot'].choices = SLOT_CHOICES

    DAYS_CHOICES = []
    now = timezone.localdate()

    for i in range(0, 3):
        day = now + timedelta(days=i)
        DAYS_CHOICES.append((f'{day}', f'{day} ({days_wrapper[i]})'))

    fecha = forms.ChoiceField(
        choices=DAYS_CHOICES,
        label='Día',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )
    slot = forms.ChoiceField(
        label='Sesión'
    )

    def clean(self):
        """Veirify availables places."""
        data = super().clean()
        slot = Slot.objects.get(pk=data.get('slot'))
        if not slot.available_places > 0:
            raise forms.ValidationError('No hay cupos disponibles para esta sesión.')
        training, is_new = UserTraining.objects.get_or_create(
            user=self.user,
            slot=slot
        )
        if not is_new:
            raise forms.ValidationError('Ya agendaste tu sesión para este día')
        return data
