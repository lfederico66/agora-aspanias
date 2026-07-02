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
