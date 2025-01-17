"""Training forms."""

from django import forms

# Models
from neural.training.models import TrainingType


days_wrapper = ["Hoy", "Mañana", "Pasado Mañana"]


class ClassesForm(forms.Form):
    """Classess form."""

    hour_choices = [(f"{h:02d}:00", f"{h:02d}:00") for h in range(5, 22)]

    training_type = forms.ModelChoiceField(
        queryset=TrainingType.objects.all(),
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )

    hour_init = forms.ChoiceField(
        label="Gonorrea",
        choices=hour_choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
    hour_end = forms.ChoiceField(
        choices=hour_choices,
        widget=forms.Select(
            attrs={
                "class": "form-control",
            }
        ),
    )
