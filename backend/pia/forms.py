"""Formularios web para edición de los 5 documentos del Plan de Vida."""
from django import forms
from django.forms import inlineformset_factory

from .models import (
    AlgoSobreMi,
    EntradaPlanApoyo,
    HistoriaDeVida,
    PlanDeApoyo,
    ProyectoDeVida,
    RespuestaHistoriaVida,
    RevisionObjetivo,
    SeccionAlgoSobreMi,
)

# ---------------------------------------------------------------------------
# Documento 1 — Historia de Vida
# ---------------------------------------------------------------------------


class HistoriaDeVidaForm(forms.ModelForm):
    class Meta:
        model = HistoriaDeVida
        fields = ["fecha_recogida", "facilitador", "texto_narrativo_final", "notas_generales"]
        widgets = {
            "fecha_recogida": forms.DateInput(attrs={"type": "date"}),
            "texto_narrativo_final": forms.Textarea(attrs={"rows": 10}),
            "notas_generales": forms.Textarea(attrs={"rows": 4}),
        }


RespuestaHistoriaVidaFormSet = inlineformset_factory(
    parent_model=HistoriaDeVida,
    model=RespuestaHistoriaVida,
    fields=["pregunta_texto", "respuesta_texto", "orden"],
    extra=0,
    can_delete=False,
    widgets={
        "pregunta_texto": forms.Textarea(attrs={"rows": 2, "readonly": "readonly", "class": "bg-slate-50"}),
        "respuesta_texto": forms.Textarea(attrs={"rows": 4}),
        "orden": forms.HiddenInput(),
    },
)


# ---------------------------------------------------------------------------
# Documento 2 — Algo sobre mí
# ---------------------------------------------------------------------------


class AlgoSobreMiForm(forms.ModelForm):
    class Meta:
        model = AlgoSobreMi
        fields = ["fecha_actualizacion", "actualizado_por"]
        widgets = {"fecha_actualizacion": forms.DateInput(attrs={"type": "date"})}


SeccionAlgoSobreMiFormSet = inlineformset_factory(
    parent_model=AlgoSobreMi,
    model=SeccionAlgoSobreMi,
    fields=["titulo", "contenido", "orden"],
    extra=0,
    can_delete=False,
    widgets={
        "titulo": forms.TextInput(attrs={"readonly": "readonly", "class": "bg-slate-50 font-medium"}),
        "contenido": forms.Textarea(attrs={"rows": 4}),
        "orden": forms.HiddenInput(),
    },
)


# ---------------------------------------------------------------------------
# Documento 3 — Revisión de objetivos
# ---------------------------------------------------------------------------


class RevisionObjetivoForm(forms.ModelForm):
    class Meta:
        model = RevisionObjetivo
        fields = [
            "anualidad", "fecha_revision", "realizada_por",
            "que_ha_logrado", "motivo_no_consecucion", "propuesta_apoyos",
        ]
        widgets = {
            "anualidad": forms.NumberInput(),
            "fecha_revision": forms.DateInput(attrs={"type": "date"}),
            "que_ha_logrado": forms.Textarea(attrs={"rows": 4}),
            "motivo_no_consecucion": forms.Textarea(attrs={"rows": 3}),
            "propuesta_apoyos": forms.Textarea(attrs={"rows": 3}),
        }


# ---------------------------------------------------------------------------
# Documento 4 — Plan de Apoyo
# ---------------------------------------------------------------------------


class PlanDeApoyoForm(forms.ModelForm):
    class Meta:
        model = PlanDeApoyo
        fields = ["fecha_realizacion", "realizado_por"]
        widgets = {"fecha_realizacion": forms.DateInput(attrs={"type": "date"})}


EntradaPlanApoyoFormSet = inlineformset_factory(
    parent_model=PlanDeApoyo,
    model=EntradaPlanApoyo,
    fields=[
        "titulo_objetivo", "actividades", "dimensiones_cdv",
        "apoyo_que", "apoyo_quien", "apoyo_cuando",
        "observaciones", "seguimiento_cuantitativo", "seguimiento_descriptivo",
        "orden",
    ],
    extra=1,  # permite añadir 1 entrada nueva al editar
    can_delete=True,
    widgets={
        "titulo_objetivo": forms.TextInput(attrs={"class": "font-medium"}),
        "actividades": forms.Textarea(attrs={"rows": 3}),
        "apoyo_que": forms.Textarea(attrs={"rows": 2}),
        "apoyo_quien": forms.Textarea(attrs={"rows": 2}),
        "apoyo_cuando": forms.Textarea(attrs={"rows": 2}),
        "observaciones": forms.Textarea(attrs={"rows": 2}),
        "seguimiento_cuantitativo": forms.Textarea(attrs={"rows": 2}),
        "seguimiento_descriptivo": forms.Textarea(attrs={"rows": 2}),
        "orden": forms.HiddenInput(),
        "dimensiones_cdv": forms.CheckboxSelectMultiple(),
    },
)


# ---------------------------------------------------------------------------
# Documento 5 — Proyecto de Vida
# ---------------------------------------------------------------------------


class ProyectoDeVidaForm(forms.ModelForm):
    class Meta:
        model = ProyectoDeVida
        fields = [
            "fecha", "elaborado_por",
            "sueno_1", "sueno_2", "sueno_3",
            "valores",
            "me_gusta_dia_a_dia", "no_me_gusta_dia_a_dia",
            "apoyos_naturales", "apoyos_profesionales", "apoyos_comunitarios",
            "hitos_historia_vida",
            "publicado_en_repriss",
        ]
        widgets = {
            "fecha": forms.DateInput(attrs={"type": "date"}),
            "sueno_1": forms.Textarea(attrs={"rows": 3}),
            "sueno_2": forms.Textarea(attrs={"rows": 3}),
            "sueno_3": forms.Textarea(attrs={"rows": 3}),
            "valores": forms.Textarea(attrs={"rows": 4}),
            "me_gusta_dia_a_dia": forms.Textarea(attrs={"rows": 4}),
            "no_me_gusta_dia_a_dia": forms.Textarea(attrs={"rows": 4}),
            "apoyos_naturales": forms.Textarea(attrs={"rows": 3}),
            "apoyos_profesionales": forms.Textarea(attrs={"rows": 3}),
            "apoyos_comunitarios": forms.Textarea(attrs={"rows": 3}),
            "hitos_historia_vida": forms.Textarea(attrs={"rows": 6}),
        }
