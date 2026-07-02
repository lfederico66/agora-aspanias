from django.contrib import admin

from .models import (
    Alergia,
    AvisoCambioProfesional,
    Cama,
    Centro,
    CertificadoDiscapacidad,
    CuidadoEnfermeria,
    EnfermedadCronica,
    FiguraDeApoyo,
    Habitacion,
    InformacionMedica,
    Medicamento,
    MedidaAntropometrica,
    MedidaDeApoyo,
    Modulo,
    NucleoFamiliar,
    OcupacionCama,
    PautaMedicacion,
    PerfilDI,
    PerfilInsercion,
    PerfilMayor,
    PersonaAtendida,
    PersonaContacto,
    ProblemaSalud,
    Profesional,
    ReconocimientoDependencia,
    Rol,
    Servicio,
    ServicioContratado,
    Vacuna,
    VinculoPersonaContacto,
)


class PerfilDIInline(admin.TabularInline):
    model = PerfilDI
    extra = 0


class PerfilMayorInline(admin.TabularInline):
    model = PerfilMayor
    extra = 0


class PerfilInsercionInline(admin.TabularInline):
    model = PerfilInsercion
    extra = 0


class ServicioContratadoInline(admin.TabularInline):
    model = ServicioContratado
    extra = 0


class VinculoContactoInline(admin.TabularInline):
    model = VinculoPersonaContacto
    extra = 0


class FiguraApoyoInline(admin.TabularInline):
    model = FiguraDeApoyo
    extra = 0


class AlergiaInlineForPersona(admin.TabularInline):
    model = Alergia
    extra = 0
    fields = ("tipo", "sustancia", "gravedad", "activa")


class EnfermedadCronicaInlineForPersona(admin.TabularInline):
    model = EnfermedadCronica
    extra = 0
    fields = ("nombre", "fecha_diagnostico", "en_seguimiento")


class PautaMedicacionInline(admin.TabularInline):
    model = PautaMedicacion
    extra = 0
    fields = ("medicamento", "dosis_desayuno", "dosis_comida", "dosis_cena", "fecha_inicio", "fecha_fin", "activa")
    autocomplete_fields = ("medicamento",)
    show_change_link = True


class OcupacionCamaInline(admin.TabularInline):
    model = OcupacionCama
    extra = 0
    fields = ("cama", "fecha_inicio", "fecha_fin", "motivo_alta", "motivo_baja")
    autocomplete_fields = ("cama",)
    show_change_link = True


@admin.register(PersonaAtendida)
class PersonaAtendidaAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_interno", "apellido_1", "apellido_2", "nombre",
        "centro_referencia", "gestor_caso", "persona_referencia", "activa",
    )
    list_filter = ("corresponsable_principal", "centro_referencia", "sexo", "gestor_caso")
    search_fields = ("codigo_interno", "nombre", "apellido_1", "apellido_2", "dni_nie")
    autocomplete_fields = ("gestor_caso", "persona_referencia")
    inlines = [
        PerfilDIInline, PerfilMayorInline, PerfilInsercionInline,
        ServicioContratadoInline, VinculoContactoInline,
        AlergiaInlineForPersona, EnfermedadCronicaInlineForPersona,
        PautaMedicacionInline, OcupacionCamaInline,
    ]
    readonly_fields = ("id", "created_at", "updated_at")
    fieldsets = (
        ("Identificación", {
            "fields": (
                "id", "codigo_interno", "nombre", "apellido_1", "apellido_2",
                "dni_nie", "fecha_nacimiento", "sexo", "nacionalidad",
            ),
        }),
        ("Dirección postal", {
            "fields": (
                "direccion_calle", "direccion_cp",
                "direccion_municipio", "direccion_provincia",
            ),
        }),
        ("Datos administrativos sanitarios", {
            "fields": (
                "numero_seguridad_social", "numero_tarjeta_sanitaria",
                "tsi_caducidad", "centro_salud",
            ),
            "description": (
                "Datos de categoría especial (RGPD art. 9). Acceso restringido."
            ),
        }),
        ("Comunicación", {
            "fields": (
                "forma_comunicacion_preferente", "idioma_preferente",
                "usa_saac", "saac_notas",
            ),
        }),
        ("Servicios y centro", {
            "fields": (
                "corresponsable_principal", "centro_referencia",
                "fecha_alta", "fecha_baja", "motivo_baja",
            ),
        }),
        ("Figuras profesionales (Protocolo Planes de Vida)", {
            "fields": ("gestor_caso", "persona_referencia"),
        }),
        ("Notas", {"fields": ("notas_relevantes",)}),
        ("Auditoría", {"fields": ("created_at", "updated_at")}),
    )


@admin.register(MedidaDeApoyo)
class MedidaDeApoyoAdmin(admin.ModelAdmin):
    list_display = ("persona", "tipo", "vigente", "revisado_at")
    list_filter = ("tipo", "vigente")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "persona__codigo_interno")
    inlines = [FiguraApoyoInline]


@admin.register(Centro)
class CentroAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "corresponsable", "municipio", "activo")
    list_filter = ("corresponsable", "activo")
    search_fields = ("codigo", "nombre")


@admin.register(Servicio)
class ServicioAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre", "tipo")
    list_filter = ("tipo",)
    search_fields = ("codigo", "nombre")


@admin.register(Profesional)
class ProfesionalAdmin(admin.ModelAdmin):
    list_display = (
        "nombre_completo", "rol_principal", "email_m365",
        "puede_ser_gestor_caso", "casos_actuales_gestor", "max_casos_asignados", "activo",
    )
    list_filter = ("activo", "rol_principal", "puede_ser_gestor_caso")
    search_fields = ("nombre_completo", "email_m365")
    filter_horizontal = ("centros_acceso",)

    def casos_actuales_gestor(self, obj):
        n = obj.casos_actuales_gestor
        if obj.sobrepasa_ratio:
            return f"⚠ {n} (sobre ratio)"
        return n
    casos_actuales_gestor.short_description = "Casos como gestor/a"


@admin.register(Rol)
class RolAdmin(admin.ModelAdmin):
    list_display = ("codigo", "nombre")
    search_fields = ("codigo", "nombre")


@admin.register(PersonaContacto)
class PersonaContactoAdmin(admin.ModelAdmin):
    list_display = ("apellido_1", "apellido_2", "nombre", "telefono", "email", "consentimiento_comunicacion")
    search_fields = ("nombre", "apellido_1", "apellido_2", "email", "telefono")


@admin.register(NucleoFamiliar)
class NucleoFamiliarAdmin(admin.ModelAdmin):
    list_display = ("nombre_referencia", "persona_referencia")
    search_fields = ("nombre_referencia",)
    filter_horizontal = ("personas_atendidas",)


@admin.register(AvisoCambioProfesional)
class AvisoCambioProfesionalAdmin(admin.ModelAdmin):
    list_display = ("detectado_at", "persona", "tipo", "profesional_anterior", "profesional_nuevo", "estado")
    list_filter = ("estado", "tipo", "detectado_at")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "persona__codigo_interno")
    readonly_fields = ("detectado_at",)
    date_hierarchy = "detectado_at"


# ---------------------------------------------------------------------------
# Discapacidad y dependencia
# ---------------------------------------------------------------------------


@admin.register(CertificadoDiscapacidad)
class CertificadoDiscapacidadAdmin(admin.ModelAdmin):
    list_display = (
        "persona", "grado_pct", "puntos_factores_sociales",
        "tipo_reconocimiento", "fecha_reconocimiento", "vigente",
    )
    list_filter = ("vigente", "tipo_reconocimiento")
    search_fields = (
        "persona__apellido_1", "persona__apellido_2",
        "persona__codigo_interno", "diagnostico_principal",
    )
    date_hierarchy = "fecha_reconocimiento"
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(ReconocimientoDependencia)
class ReconocimientoDependenciaAdmin(admin.ModelAdmin):
    list_display = (
        "persona", "grado", "puntos_bvd",
        "fecha_resolucion", "tipo_beneficio", "vigente",
    )
    list_filter = ("vigente", "grado", "tipo_beneficio")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "persona__codigo_interno")
    date_hierarchy = "fecha_resolucion"
    readonly_fields = ("id", "created_at", "updated_at")


# ---------------------------------------------------------------------------
# Información médica (categoría especial RGPD art. 9)
# ---------------------------------------------------------------------------


@admin.register(InformacionMedica)
class InformacionMedicaAdmin(admin.ModelAdmin):
    list_display = ("persona", "grupo_sanguineo", "vacunacion_permitida", "updated_at")
    list_filter = ("grupo_sanguineo", "vacunacion_permitida")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "persona__codigo_interno")
    readonly_fields = ("updated_at", "updated_by")


@admin.register(Alergia)
class AlergiaAdmin(admin.ModelAdmin):
    list_display = ("persona", "tipo", "sustancia", "gravedad", "activa", "fecha_diagnostico")
    list_filter = ("tipo", "gravedad", "activa")
    search_fields = ("sustancia", "persona__apellido_1", "persona__apellido_2")


@admin.register(EnfermedadCronica)
class EnfermedadCronicaAdmin(admin.ModelAdmin):
    list_display = ("persona", "nombre", "fecha_diagnostico", "en_seguimiento")
    list_filter = ("en_seguimiento",)
    search_fields = ("nombre", "persona__apellido_1", "persona__apellido_2")


@admin.register(MedidaAntropometrica)
class MedidaAntropometricaAdmin(admin.ModelAdmin):
    list_display = (
        "persona", "fecha", "peso_kg", "talla_cm", "imc",
        "tension_sistolica", "tension_diastolica", "pulso", "temperatura",
    )
    list_filter = ("fecha",)
    date_hierarchy = "fecha"
    search_fields = ("persona__apellido_1", "persona__apellido_2", "persona__codigo_interno")
    readonly_fields = ("imc", "created_at")


@admin.register(Vacuna)
class VacunaAdmin(admin.ModelAdmin):
    list_display = ("persona", "vacuna", "fecha", "dosis", "estacional")
    list_filter = ("estacional", "vacuna")
    search_fields = ("vacuna", "persona__apellido_1", "persona__apellido_2")
    date_hierarchy = "fecha"


@admin.register(CuidadoEnfermeria)
class CuidadoEnfermeriaAdmin(admin.ModelAdmin):
    list_display = ("persona", "updated_at", "updated_by")
    search_fields = ("persona__apellido_1", "persona__apellido_2", "persona__codigo_interno")
    readonly_fields = ("updated_at", "updated_by")
    fieldsets = (
        (None, {"fields": ("persona",)}),
        ("Dimensiones del cuidado", {
            "fields": (
                "respiracion", "audicion", "vision",
                "alimentacion", "sueno_descanso", "eliminacion",
                "movilidad", "autonomia_abvd", "conducta", "cuidados_piel",
                "observaciones",
            ),
        }),
        ("Auditoría", {"fields": ("updated_at", "updated_by")}),
    )


@admin.register(ProblemaSalud)
class ProblemaSaludAdmin(admin.ModelAdmin):
    list_display = (
        "persona", "descripcion", "tipo", "especialista",
        "responsable_interno", "estado", "fecha_apertura",
    )
    list_filter = ("estado", "tipo")
    search_fields = (
        "descripcion", "especialista",
        "persona__apellido_1", "persona__apellido_2",
    )
    date_hierarchy = "fecha_apertura"
    autocomplete_fields = ("responsable_interno",)


# ---------------------------------------------------------------------------
# Medicación
# ---------------------------------------------------------------------------


@admin.register(Medicamento)
class MedicamentoAdmin(admin.ModelAdmin):
    list_display = ("nombre_comercial", "dosis", "principio_activo", "familia", "via_administracion", "activo")
    list_filter = ("familia", "via_administracion", "activo")
    search_fields = ("nombre_comercial", "principio_activo")


@admin.register(PautaMedicacion)
class PautaMedicacionAdmin(admin.ModelAdmin):
    list_display = (
        "persona", "medicamento", "dosificacion_texto",
        "fecha_inicio", "fecha_fin", "prescriptor", "activa",
    )
    list_filter = ("activa", "medicamento__familia", "fecha_inicio")
    search_fields = (
        "medicamento__nombre_comercial", "medicamento__principio_activo",
        "persona__apellido_1", "persona__apellido_2",
    )
    autocomplete_fields = ("medicamento", "problema_salud")
    date_hierarchy = "fecha_inicio"
    readonly_fields = ("id", "created_at", "updated_at", "created_by")


# ---------------------------------------------------------------------------
# Alojamiento físico
# ---------------------------------------------------------------------------


class HabitacionInline(admin.TabularInline):
    model = Habitacion
    extra = 0
    fields = ("numero", "tipo", "con_bano_propio", "adaptada_movilidad_reducida", "activa")
    show_change_link = True


class CamaInline(admin.TabularInline):
    model = Cama
    extra = 0
    fields = ("identificador", "articulada", "barandillas", "grua_compatible", "activa")
    show_change_link = True


@admin.register(Modulo)
class ModuloAdmin(admin.ModelAdmin):
    list_display = ("centro", "codigo", "nombre", "activo")
    list_filter = ("centro", "activo")
    search_fields = ("nombre", "codigo", "centro__nombre")
    inlines = [HabitacionInline]


@admin.register(Habitacion)
class HabitacionAdmin(admin.ModelAdmin):
    list_display = (
        "centro", "modulo", "numero", "tipo",
        "con_bano_propio", "adaptada_movilidad_reducida", "activa",
    )
    list_filter = ("centro", "modulo", "tipo", "activa", "adaptada_movilidad_reducida")
    search_fields = ("numero", "centro__nombre")
    inlines = [CamaInline]


@admin.register(Cama)
class CamaAdmin(admin.ModelAdmin):
    list_display = (
        "habitacion", "identificador",
        "articulada", "barandillas", "grua_compatible", "activa",
    )
    list_filter = ("activa", "articulada", "barandillas")
    search_fields = ("identificador", "habitacion__numero", "habitacion__centro__nombre")
    autocomplete_fields = ("habitacion",)


@admin.register(OcupacionCama)
class OcupacionCamaAdmin(admin.ModelAdmin):
    list_display = (
        "persona", "cama", "fecha_inicio", "fecha_fin",
        "motivo_alta", "motivo_baja",
    )
    list_filter = ("motivo_alta", "motivo_baja")
    search_fields = (
        "persona__apellido_1", "persona__apellido_2", "persona__codigo_interno",
        "cama__identificador",
    )
    autocomplete_fields = ("persona", "cama")
    date_hierarchy = "fecha_inicio"
    readonly_fields = ("id", "created_at", "created_by")


admin.site.site_header = "ÁGORA — Administración"
admin.site.site_title = "ÁGORA"
admin.site.index_title = "Gestión del sistema"
