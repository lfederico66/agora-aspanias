"""Formulario web para crear y editar citas de la agenda."""
from django import forms

from .models import Cita


class CitaForm(forms.ModelForm):
    class Meta:
        model = Cita
        fields = [
            "persona", "profesionales", "tipo",
            "inicio", "fin",
            "ubicacion", "estado",
            "notas", "notificada_a_familia",
        ]
        widgets = {
            "inicio": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "fin": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "ubicacion": forms.TextInput(),
            "notas": forms.Textarea(attrs={"rows": 3}),
            "profesionales": forms.CheckboxSelectMultiple(),
        }

    def clean(self):
        cleaned = super().clean()
        inicio = cleaned.get("inicio")
        fin = cleaned.get("fin")
        if inicio and fin and fin <= inicio:
            self.add_error("fin", "La hora de fin debe ser posterior a la de inicio.")
        return cleaned
