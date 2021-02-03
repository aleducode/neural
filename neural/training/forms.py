"""Training forms."""

from django import forms
from django.utils import timezone
from datetime import timedelta
from neural.training.models import UserTraining, Slot, Space, UserTemperature
from django.utils.translation import gettext as _

days_wrapper = ['Hoy', 'Mañana', 'Pasado Mañana']


class SchduleForm(forms.Form):
    """Schedule form."""

    def __init__(self, *args, **kwargs):
        SLOT_CHOICES = [('', 'Seleccionar')]
        if 'user' in kwargs:
            self.user = kwargs.pop('user')

        if 'now' in kwargs:
            self.now = kwargs.pop('now')
        super().__init__(*args, **kwargs)
        self.fields['slot'].widget = forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
        self.fields['slot'].choices = SLOT_CHOICES
        DAYS_CHOICES = []

        for i in range(0, 3):
            day = self.now + timedelta(days=i)
            if day.isoweekday() != 7:
                day_name = _(day.strftime("%A"))
                DAYS_CHOICES.append((f'{day}', f'{day} ({day_name})'))
        self.fields['fecha'].choices = DAYS_CHOICES

    fecha = forms.ChoiceField(
        choices=[],
        label='Día',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )
    space = forms.ModelChoiceField(
        queryset=Space.objects.all().order_by('id'),
        label='Espacio de trabajo',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'disabled': 'disabled'
            }
        )
    )
    slot = forms.ModelChoiceField(
        queryset=Slot.objects.all().order_by('id'),
        label='Sesión',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
                'disabled': 'disabled'
            }
        )
    )
    classes = forms.ChoiceField(
        choices=Slot.TrainingType.choices,
        label='Clases',
        widget=forms.Select(
            attrs={
                'class': 'form-control',
            }
        )
    )

    def clean(self):
        """Veirify availables places."""
        data = super().clean()
        if not self.errors:
            slot = data.get('slot')
            if not slot.available_places > 0:
                raise forms.ValidationError('No hay cupos disponibles para esta sesión.')
            # Check work spaces availability
            if UserTraining.objects.filter(slot=slot, space=data.get('space')).exists():
                raise forms.ValidationError(
                    'Este espacio de trabajo ya ha sido seleccionado por alguien mas, intenta seleccionar otro.')
            training_already_schedule = UserTraining.objects.filter(
                user=self.user,
                slot=slot,
                status=UserTraining.Status.CONFIRMED
            ).exists()
            if training_already_schedule:
                raise forms.ValidationError('Ya agendaste tu sesión para este día')
        return data

    def save(self):
        data = self.cleaned_data
        training = UserTraining.objects.create(
            user=self.user,
            slot=data.get('slot'),
            space=data.get('space'),
        )
        return training


class TemperatureInputForm(forms.Form):

    def __init__(self, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)
    temperature = forms.FloatField(
        min_value=30,
        max_value=40,
        widget=forms.NumberInput(attrs={
            'class': 'form-control form-control-lg',
        }))

    def save(self):
        data = self.cleaned_data
        training = UserTemperature.objects.create(
            user=self.user,
            temperature=data.get('temperature'),
        )
        return training
