"""Training forms."""

from django import forms

# Models
from neural.training.models import ImagePopUp, TrainingType


days_wrapper = ["Hoy", "Mañana", "Pasado Mañana"]


class ImagePopUpForm(forms.ModelForm):
    """Admin form image pop up."""

    def clean(self):
        """Check min and max lenght."""
        is_active = ImagePopUp.objects.filter(is_active=True).count()
        if is_active > 0:
            raise forms.ValidationError(
                "Ya hay una imagen con estado activo, elimina está si quieres agregar una nueva."
            )
        return super().clean()

    class Meta:
        model = ImagePopUp
        fields = "__all__"


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
