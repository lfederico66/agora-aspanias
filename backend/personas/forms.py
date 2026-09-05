"""Formularios web de personas atendidas."""
from django import forms

from .models import PersonaAtendida


class PersonaAtendidaForm(forms.ModelForm):
    """Formulario único para alta y edición de personas atendidas.

    Los perfiles por colectivo, medida de apoyo, contactos y servicios contratados
    se editan desde bloques específicos en la ficha o desde el admin.
    """

    class Meta:
        model = PersonaAtendida
        fields = [
            "codigo_interno",
            "nombre", "apellido_1", "apellido_2",
            "dni_nie",
            "fecha_nacimiento", "sexo", "nacionalidad",
            "direccion_calle", "direccion_cp",
            "direccion_municipio", "direccion_provincia",
            # Datos administrativos sanitarios (v0.11) — NUSS/TSI cifrados
            "numero_seguridad_social", "numero_tarjeta_sanitaria",
            "tsi_caducidad", "centro_salud",
            # Comunicación (v0.11)
            "forma_comunicacion_preferente", "idioma_preferente",
            "usa_saac", "saac_notas",
            "centro_referencia", "corresponsable_principal",
            "gestor_caso", "persona_referencia",
            "fecha_alta", "fecha_baja", "motivo_baja",
            "notas_relevantes",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}),
            "fecha_alta": forms.DateInput(attrs={"type": "date"}),
            "fecha_baja": forms.DateInput(attrs={"type": "date"}),
            "tsi_caducidad": forms.DateInput(attrs={"type": "date"}),
            "saac_notas": forms.Textarea(attrs={"rows": 2}),
            "notas_relevantes": forms.Textarea(attrs={"rows": 3}),
        }
        help_texts = {
            "codigo_interno": "Si lo dejas en blanco se genera automáticamente: CENTRO-AÑO-NNNNN.",
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Marca obligatorios sin asterisco redundante
        self.fields["codigo_interno"].required = False
        # Restringir gestor_caso a profesionales habilitados
        self.fields["gestor_caso"].queryset = self.fields["gestor_caso"].queryset.filter(
            puede_ser_gestor_caso=True, activo=True,
        )
        self.fields["persona_referencia"].queryset = self.fields["persona_referencia"].queryset.filter(
            activo=True,
        )

    def clean(self):
        cleaned = super().clean()
        fecha_baja = cleaned.get("fecha_baja")
        motivo_baja = cleaned.get("motivo_baja")
        if fecha_baja and not motivo_baja:
            self.add_error("motivo_baja", "Indica el motivo si registras una fecha de baja.")
        if motivo_baja and not fecha_baja:
            self.add_error("fecha_baja", "Indica la fecha si registras un motivo de baja.")
        return cleaned


class CuidadoEnfermeriaForm(forms.ModelForm):
    """Plan de salud-cuidados (petición Dirección Fuentecillas, jun 2026)."""

    class Meta:
        from .models import CuidadoEnfermeria

        model = CuidadoEnfermeria
        fields = [
            "respiracion", "audicion", "vision", "alimentacion",
            "sueno_descanso", "eliminacion", "movilidad", "autonomia_abvd",
            "conducta", "cuidados_piel", "observaciones",
        ]
        labels = {
            "respiracion": "Respiración",
            "audicion": "Audición",
            "vision": "Visión",
            "alimentacion": "Alimentación",
            "sueno_descanso": "Sueño y descanso",
            "eliminacion": "Eliminación",
            "movilidad": "Movilidad",
            "autonomia_abvd": "Autonomía ABVD",
            "conducta": "Conducta",
            "cuidados_piel": "Cuidados de la piel",
            "observaciones": "Observaciones",
        }
        widgets = {
            campo: forms.Textarea(attrs={
                "rows": 2,
                "class": "w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
                         "focus:outline-none focus:border-emerald-500",
            })
            for campo in fields
        }


class DatosBaseForm(forms.ModelForm):
    """Edición inline de los datos base de la ficha (P1 pre-piloto).

    Subconjunto de PersonaAtendidaForm: identidad, dirección, comunicación
    y administrativos sanitarios. Centro, gestora y fechas de alta/baja se
    cambian por sus flujos propios, no inline.
    """

    class Meta:
        model = PersonaAtendida
        fields = [
            "nombre", "apellido_1", "apellido_2", "dni_nie",
            "fecha_nacimiento", "sexo", "nacionalidad",
            "direccion_calle", "direccion_cp",
            "direccion_municipio", "direccion_provincia",
            "forma_comunicacion_preferente", "idioma_preferente",
            "usa_saac", "saac_notas",
            "numero_seguridad_social", "numero_tarjeta_sanitaria",
            "tsi_caducidad", "centro_salud",
        ]
        widgets = {
            "fecha_nacimiento": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "tsi_caducidad": forms.DateInput(attrs={"type": "date"}, format="%Y-%m-%d"),
            "saac_notas": forms.TextInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        clase = ("w-full rounded-lg border border-slate-300 px-3 py-2 text-sm "
                 "focus:outline-none focus:border-emerald-500")
        for nombre, campo in self.fields.items():
            if not isinstance(campo.widget, forms.CheckboxInput):
                campo.widget.attrs.setdefault("class", clase)
