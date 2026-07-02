"""Formularios web para intervenciones y valoraciones."""
from django import forms

from .models import Intervencion, Valoracion


class IntervencionForm(forms.ModelForm):
    class Meta:
        model = Intervencion
        fields = [
            "persona", "profesional", "tipo",
            "fecha_hora",
            "descripcion",
            "objetivo_vinculado",
            "confidencialidad",
        ]
        widgets = {
            "fecha_hora": forms.DateTimeInput(attrs={"type": "datetime-local"}),
            "descripcion": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        persona = kwargs.pop("persona", None)
        super().__init__(*args, **kwargs)
        # Restringir objetivos a los del Plan de Vida vigente de la persona
        if persona is not None:
            from pia.models import Objetivo, PlanDeVida
            self.fields["objetivo_vinculado"].queryset = Objetivo.objects.filter(
                plan_vida__persona=persona,
                plan_vida__estado=PlanDeVida.Estado.VIGENTE,
            )
            self.fields["persona"].initial = persona


class ValoracionForm(forms.ModelForm):
    class Meta:
        model = Valoracion
        fields = [
            "persona", "instrumento", "fecha",
            "aplicado_por", "observaciones",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        persona = kwargs.pop("persona", None)
        super().__init__(*args, **kwargs)
        if persona is not None:
            self.fields["persona"].initial = persona
