"""Training forms."""

from datetime import timedelta, datetime, time
from typing import Any
from django import forms
from django.utils.translation import gettext as _

# Models
from neural.training.models import UserTraining, Slot, Space, ImagePopUp, TrainingType


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
    # classes = forms.ChoiceField(
    #     choices=Slot.TrainingType.choices,
    #     label='Clases',
    #     widget=forms.Select(
    #         attrs={
    #             'class': 'form-control',
    #         }
    #     )
    # )

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
                slot__date=slot.date,
                slot__training_type=slot.training_type,
                status=UserTraining.Status.CONFIRMED
            ).exists()
            if training_already_schedule:
                raise forms.ValidationError(
                    'Ya agendaste tu sesión para este día, debes cancelar si quieres agendar de nuevo.')
        return data

    def save(self):
        data = self.cleaned_data
        training = UserTraining.objects.create(
            user=self.user,
            slot=data.get('slot'),
            space=data.get('space'),
        )
        return training


class ImagePopUpForm(forms.ModelForm):
    """Admin form image pop up."""

    def clean(self):
        """Check min and max lenght."""
        is_active = ImagePopUp.objects.filter(is_active=True).count()
        if is_active > 0:
            raise forms.ValidationError("Ya hay una imagen con estado activo, elimina está si quieres agregar una nueva.")
        return super().clean()

    class Meta:
        model = ImagePopUp
        fields = '__all__'


class ClassesForm(forms.Form):
    """Classess form."""

    hour_choices = [(f'{h:02d}:00', f'{h:02d}:00') for h in range(5, 22)]

    training_type = forms.ModelChoiceField(
        queryset=TrainingType.objects.all(),
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )

    hour_init = forms.ChoiceField(
        label="Gonorrea",
        choices=hour_choices,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
    hour_end = forms.ChoiceField(
        choices=hour_choices,
        widget=forms.Select(attrs={
            'class': 'form-control',
        })
    )
