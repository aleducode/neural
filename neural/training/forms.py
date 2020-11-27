"""Training forms."""

from django import forms
from django.forms.widgets import NumberInput
from django.utils import timezone
from datetime import timedelta
from neural.training.models import UserTraining, Slot, Space, Temperature


days_wrapper = ['Hoy', 'Mañana', 'Pasado Mañana']


class SchduleForm(forms.Form):
    """Schedule form."""

    def __init__(self, request=None, *args, **kwargs):
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
                DAYS_CHOICES.append((f'{day}', f'{day} ({days_wrapper[i]})'))
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
        slot = data.get('slot')
        if not slot.available_places > 0:
            raise forms.ValidationError('No hay cupos disponibles para esta sesión.')
        training, is_new = UserTraining.objects.get_or_create(
            user=self.user,
            slot=slot,
            defaults={
                'space': data.get('space')
            }
        )
        if not is_new:
            raise forms.ValidationError('Ya agendaste tu sesión para este día')
        return data

class TemperatureForm(forms.Form):
    """Temperature registry."""

    def __init__(self, request=None, *args, **kwargs):
        if 'user' in kwargs:
            self.user = kwargs.pop('user')
        super().__init__(*args, **kwargs)


    temperature = forms.FloatField(       
        label= 'Temperatura',
        required=True,
        widget= NumberInput
        )
    
    def clean(self):
        """Validaton Temperature."""
        data = super().clean()
        temperature = data ['temperature']

        if temperature > 37:
            raise forms.ValidationError('No puedes realizar tu entrenamiento.')
        return data
    def save(self):
        data = self.cleaned_data['temperature']
        user = self.user
        Temperature.objects.create(
            user=user,
            temperature=data
        )
        return data
        
