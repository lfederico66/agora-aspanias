"""Carga datos sintéticos de prueba para los cuatro colectivos.

ATENCIÓN — Solo datos generados por Faker. Cero datos reales.
Uso: python manage.py cargar_datos_sinteticos [--personas 20]
"""
import random
from datetime import date, datetime, time, timedelta

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils import timezone
from faker import Faker

from agenda.models import Cita
from indicadores.models import Indicador
from intervenciones.models import Intervencion, TipoIntervencion
from personas.models import (
    Centro,
    FiguraDeApoyo,
    MedidaDeApoyo,
    NucleoFamiliar,
    PerfilDI,
    PerfilInsercion,
    PerfilMayor,
    PersonaAtendida,
    PersonaContacto,
    Rol,
    Servicio,
    ServicioContratado,
    VinculoPersonaContacto,
)
from pia.models import (
    DIMENSIONES_CDV_SCHALOCK,
    PREGUNTAS_HISTORIA_VIDA,
    SECCIONES_ALGO_SOBRE_MI,
    AlgoSobreMi,
    CambioSignificativo,
    DimensionCalidadVida,
    DocumentoPlanDeVida,
    EntradaPlanApoyo,
    HistoriaDeVida,
    Objetivo,
    PlanDeApoyo,
    PlanDeVida,
    ProyectoDeVida,
    RespuestaHistoriaVida,
    RevisionObjetivo,
    SeccionAlgoSobreMi,
)

fake = Faker("es_ES")

CENTROS_DEMO = [
    {"codigo": "FUE", "nombre": "Centro Fuentecillas", "corresponsable": "fundacion_aspanias_burgos", "municipio": "Burgos"},
    {"codigo": "LAR", "nombre": "Lara Río Arlanza", "corresponsable": "fundacion_aspanias_burgos", "municipio": "Lara"},
    {"codigo": "SAL", "nombre": "Residencia Salas de los Infantes", "corresponsable": "aspaniasmerc", "municipio": "Salas de los Infantes"},
    {"codigo": "VIL", "nombre": "Residencia Villadiego", "corresponsable": "aspaniasmerc", "municipio": "Villadiego"},
    {"codigo": "CEE", "nombre": "CEE CISA Burgos", "corresponsable": "fundacion_aspanias_burgos", "municipio": "Burgos"},
]

SERVICIOS_DEMO = [
    {"codigo": "RES_DI", "nombre": "Residencia DI", "tipo": "residencia"},
    {"codigo": "CD_DI", "nombre": "Centro de día DI", "tipo": "centro_dia"},
    {"codigo": "VIV", "nombre": "Vivienda", "tipo": "vivienda"},
    {"codigo": "OCU", "nombre": "Centro ocupacional", "tipo": "ocupacional"},
    {"codigo": "RES_MAY", "nombre": "Residencia mayores", "tipo": "residencia"},
    {"codigo": "SAD", "nombre": "Servicio de ayuda a domicilio", "tipo": "sad"},
    {"codigo": "CEE", "nombre": "Centro Especial de Empleo", "tipo": "cee"},
    {"codigo": "EMP", "nombre": "Empleo con apoyo", "tipo": "empleo_apoyo"},
]

ROLES_DEMO = [
    {"codigo": "TS", "nombre": "Trabajadora social"},
    {"codigo": "PSI", "nombre": "Psicóloga"},
    {"codigo": "TO", "nombre": "Terapeuta ocupacional"},
    {"codigo": "DUE", "nombre": "Diplomado en Enfermería"},
    {"codigo": "MON", "nombre": "Monitor/a"},
    {"codigo": "FIS", "nombre": "Fisioterapeuta"},
    {"codigo": "DIR", "nombre": "Dirección de centro"},
]

TIPOS_INTERVENCION_DEMO = [
    {"codigo": "SES_TO", "nombre": "Sesión TO individual", "color": "blue"},
    {"codigo": "SES_PSI", "nombre": "Sesión psicológica individual", "color": "blue"},
    {"codigo": "ENT_FAM", "nombre": "Entrevista familiar", "color": "emerald"},
    {"codigo": "REV_PIA", "nombre": "Revisión PIA multipro", "color": "amber"},
    {"codigo": "CONS_DUE", "nombre": "Control sanitario rutinario", "color": "rose"},
    {"codigo": "COM_FAM", "nombre": "Comunicación con familia (CERCA)", "color": "slate"},
    {"codigo": "VAL", "nombre": "Aplicación de valoración", "color": "purple"},
]

OBJETIVOS_DEMO = [
    ("salud", "Tomar la medicación por la mañana sin recordatorio", "3 semanas seguidas sin aviso del personal", "Pastillero con dibujos · alarma", "alta"),
    ("salud", "Asistir a las revisiones del dentista", "Dos citas realizadas al año", "Acompañamiento de monitor/a", "media"),
    ("autonomia", "Preparar mi desayuno los días de diario", "4 desayunos preparados a la semana sin supervisión", "Plantilla visual de pasos", "alta"),
    ("autonomia", "Decidir qué ropa ponerme cada día", "Decisión propia 5 días por semana", "Armario organizado por días", "media"),
    ("relaciones", "Mantener el contacto con el grupo de amistad", "1 actividad al mes con el grupo", "Recordatorio en la agenda", "media"),
    ("ocio", "Participar en el taller de pintura semanal", "Asistencia ≥ 80%", "Recordatorio · transporte", "baja"),
    ("formacion", "Completar el curso de manipulado en CEE", "Curso aprobado", "Apoyo de preparador laboral", "alta"),
    ("empleo", "Mantener el puesto actual con autonomía progresiva", "Evaluación trimestral favorable", "Seguimiento por preparador", "alta"),
]

INDICADORES_DEMO = [
    {"codigo": "PERS_ACTIV", "nombre": "Personas atendidas activas", "unidad": "absoluto"},
    {"codigo": "OCUP_RES", "nombre": "Ocupación residencias", "unidad": "porcentaje", "objetivo_valor": 92},
    {"codigo": "PIA_REV", "nombre": "PIAs revisados en plazo", "unidad": "porcentaje", "objetivo_valor": 90},
    {"codigo": "INT_MES", "nombre": "Intervenciones del mes", "unidad": "absoluto"},
    {"codigo": "FAM_NOT", "nombre": "Tasa de notificación a familias", "unidad": "porcentaje", "objetivo_valor": 95},
    {"codigo": "BIT_ACC", "nombre": "Accesos a fichas (bitácora)", "unidad": "absoluto"},
]


class Command(BaseCommand):
    help = "Carga datos sintéticos de prueba para los cuatro colectivos."

    def add_arguments(self, parser):
        parser.add_argument("--personas", type=int, default=20, help="Nº de personas atendidas a generar.")

    @transaction.atomic
    def handle(self, *args, **opts):
        n = opts["personas"]
        self.stdout.write(self.style.NOTICE(f"Generando {n} personas sintéticas..."))

        centros = self._cargar_catalogos(Centro, CENTROS_DEMO, "codigo")
        servicios = self._cargar_catalogos(Servicio, SERVICIOS_DEMO, "codigo")
        self._cargar_catalogos(Rol, ROLES_DEMO, "codigo")
        tipos_inter = self._cargar_catalogos(TipoIntervencion, TIPOS_INTERVENCION_DEMO, "codigo")
        self._cargar_catalogos(Indicador, INDICADORES_DEMO, "codigo")
        # 8 dimensiones de Calidad de Vida (modelo Schalock — plantilla oficial ANEXO 4)
        for codigo, nombre, descripcion, orden in DIMENSIONES_CDV_SCHALOCK:
            DimensionCalidadVida.objects.get_or_create(
                codigo=codigo,
                defaults={"nombre": nombre, "descripcion": descripcion, "orden": orden},
            )

        # Crear pool de gestores/as y personas de referencia (cumpliendo ratio 30 casos)
        pool_profesionales = self._crear_pool_profesionales(centros, n_personas=n)

        for i in range(n):
            persona = self._generar_persona(i + 1, centros, servicios, pool_profesionales)
            self._generar_plan_vida(persona)
            self._generar_intervenciones(persona, tipos_inter)
            self._generar_citas(persona)
            self._generar_cambios_significativos(persona)

        total = PersonaAtendida.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Listo. Personas: {total} · Planes de Vida: {PlanDeVida.objects.count()} · "
            f"Objetivos: {Objetivo.objects.count()} · "
            f"Revisiones: {RevisionObjetivo.objects.count()} · "
            f"Historias de Vida: {HistoriaDeVida.objects.count()} · "
            f"Algo sobre mí: {AlgoSobreMi.objects.count()} · "
            f"Planes de Apoyo: {PlanDeApoyo.objects.count()} · "
            f"Proyectos de Vida: {ProyectoDeVida.objects.count()} · "
            f"Intervenciones: {Intervencion.objects.count()} · Citas: {Cita.objects.count()} · "
            f"Cambios significativos: {CambioSignificativo.objects.count()}."
        ))

    def _crear_pool_profesionales(self, centros, n_personas):
        """Crea un pool de profesionales para gestor/a de caso y persona de referencia.

        Respeta el ratio 30 casos del protocolo: 1 gestor/a por cada 25 personas (margen).
        """
        from django.contrib.auth import get_user_model

        from personas.models import Profesional, Rol

        User = get_user_model()
        rol_ts = Rol.objects.filter(codigo="TS").first()
        rol_psi = Rol.objects.filter(codigo="PSI").first()
        rol_to = Rol.objects.filter(codigo="TO").first()
        rol_mon = Rol.objects.filter(codigo="MON").first()

        n_gestores = max(2, (n_personas // 25) + 1)
        n_referencia = max(3, n_personas // 8)

        gestores = []
        nombres_gestores = [
            ("María", "Ruiz", "Pérez", rol_ts, True),
            ("Carlos", "García", "López", rol_psi, True),
            ("Lucía", "Martínez", "Sanz", rol_to, True),
            ("Beatriz", "Hernando", "Olalla", rol_ts, True),
            ("Jorge", "Pérez", "Iglesias", rol_psi, True),
        ]
        for i in range(n_gestores):
            n_idx = i % len(nombres_gestores)
            n_extra = i // len(nombres_gestores)
            nombre, ap1, ap2, rol, gestor_flag = nombres_gestores[n_idx]
            sufijo = f"_{n_extra}" if n_extra > 0 else ""
            username = f"gestor_{nombre.lower()}{sufijo}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={"email": f"{username}@aspaniasburgos.com", "first_name": nombre, "last_name": ap1},
            )
            prof, _ = Profesional.objects.get_or_create(
                user=user,
                defaults={
                    "nombre_completo": f"{nombre} {ap1} {ap2}",
                    "rol_principal": rol,
                    "email_m365": f"{username}@aspaniasburgos.com",
                    "puede_ser_gestor_caso": True,
                    "max_casos_asignados": 30,
                    "activo": True,
                },
            )
            gestores.append(prof)

        # Personas de referencia (perfil más operativo, monitores y técnicos)
        referencias = []
        for i in range(n_referencia):
            username = f"referencia_{i+1}"
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={
                    "email": f"{username}@aspaniasburgos.com",
                    "first_name": fake.first_name(),
                    "last_name": fake.last_name(),
                },
            )
            prof, _ = Profesional.objects.get_or_create(
                user=user,
                defaults={
                    "nombre_completo": f"{user.first_name} {user.last_name}",
                    "rol_principal": random.choice([rol_mon, rol_to, rol_psi]),
                    "email_m365": f"{username}@aspaniasburgos.com",
                    "activo": True,
                },
            )
            referencias.append(prof)

        return {"gestores": gestores, "referencias": referencias}

    def _cargar_catalogos(self, modelo, datos, key):
        creados = {}
        for d in datos:
            obj, _ = modelo.objects.get_or_create(**{key: d[key]}, defaults=d)
            creados[d[key]] = obj
        return creados

    def _generar_persona(self, idx, centros, servicios, pool_profesionales=None):
        colectivo = random.choices(
            ["di", "mayor", "insercion", "familia"],
            weights=[40, 35, 15, 10],
        )[0]

        if colectivo == "mayor":
            centro = random.choice([centros["SAL"], centros["VIL"]])
            corresponsable = "aspaniasmerc"
            edad = random.randint(70, 95)
        elif colectivo == "insercion":
            centro = centros["CEE"]
            corresponsable = "fundacion_aspanias_burgos"
            edad = random.randint(20, 55)
        else:
            centro = random.choice([centros["FUE"], centros["LAR"]])
            corresponsable = "fundacion_aspanias_burgos"
            edad = random.randint(18, 70)

        sexo = random.choice(["M", "F"])
        if sexo == "M":
            nombre = fake.first_name_male()
        else:
            nombre = fake.first_name_female()

        fecha_nac = date.today() - timedelta(days=edad * 365 + random.randint(0, 364))
        fecha_alta = fake.date_between(start_date="-10y", end_date="-3m")

        # Asignación de gestor/a de caso (respetando ratio 30) y persona de referencia
        gestor = None
        referencia = None
        if pool_profesionales:
            gestores_disponibles = [
                g for g in pool_profesionales["gestores"] if g.casos_actuales_gestor < g.max_casos_asignados
            ]
            if gestores_disponibles:
                gestor = min(gestores_disponibles, key=lambda g: g.casos_actuales_gestor)
            if pool_profesionales["referencias"]:
                referencia = random.choice(pool_profesionales["referencias"])

        persona = PersonaAtendida.objects.create(
            codigo_interno=f"{centro.codigo}-2026-{idx:05d}",
            nombre=nombre,
            apellido_1=fake.last_name(),
            apellido_2=fake.last_name(),
            dni_nie="",
            fecha_nacimiento=fecha_nac,
            sexo=sexo,
            nacionalidad="ES",
            direccion_calle=fake.street_address(),
            direccion_cp=fake.postcode(),
            direccion_municipio=centro.municipio,
            direccion_provincia="Burgos",
            corresponsable_principal=corresponsable,
            centro_referencia=centro,
            gestor_caso=gestor,
            persona_referencia=referencia,
            fecha_alta=fecha_alta,
            notas_relevantes="",
        )

        self._anadir_perfil(persona, colectivo, fecha_alta)
        self._anadir_medida_apoyo(persona, colectivo)
        self._anadir_servicio_contratado(persona, centro, servicios, colectivo, fecha_alta, corresponsable)
        self._anadir_contacto(persona)
        return persona

    def _anadir_perfil(self, persona, colectivo, inicio):
        if colectivo == "di" or colectivo == "familia":
            PerfilDI.objects.create(
                persona=persona,
                tipo_discapacidad=random.choice(["leve", "moderada", "severa", "no_valorada"]),
                grado_discapacidad_pct=random.choice([33, 45, 65, 75, 85]),
                fecha_reconocimiento=inicio - timedelta(days=random.randint(0, 3650)),
                inicio_at=inicio,
            )
        elif colectivo == "mayor":
            PerfilMayor.objects.create(
                persona=persona,
                grado_dependencia=random.choice(["I", "II", "III"]),
                fecha_valoracion_bvd=inicio - timedelta(days=random.randint(0, 1095)),
                inicio_at=inicio,
            )
        elif colectivo == "insercion":
            PerfilInsercion.objects.create(
                persona=persona,
                programa=random.choice(["cee", "empleo_apoyo", "insercion"]),
                entidad_empleadora="CISA EMPLEA",
                puesto_actual=random.choice(["Operario/a montaje", "Auxiliar de jardinería", "Auxiliar de limpieza", "Manipulado"]),
                nivel_apoyo_requerido=random.choice(["bajo", "medio", "alto"]),
                inicio_at=inicio,
            )

    def _anadir_medida_apoyo(self, persona, colectivo):
        if colectivo == "mayor":
            tipo = random.choice(["sin_medida", "apoyo_voluntario", "apoyo_judicial", "apoyo_hecho"])
        elif colectivo == "insercion":
            tipo = random.choice(["sin_medida", "apoyo_voluntario"])
        else:
            tipo = random.choice(["apoyo_voluntario", "apoyo_judicial", "apoyo_hecho"])
        MedidaDeApoyo.objects.create(
            persona=persona,
            tipo=tipo,
            ambito_apoyos=("Decisiones económicas relevantes y consentimientos sanitarios."
                          if tipo != "sin_medida" else ""),
            ambito_capacidad_conservada=("Decisiones cotidianas, ocio y relaciones personales."
                                       if tipo != "sin_medida" else ""),
            vigente=True,
        )

    def _anadir_servicio_contratado(self, persona, centro, servicios, colectivo, inicio, corresponsable):
        servicio_codigo = {
            "di": random.choice(["RES_DI", "CD_DI", "VIV", "OCU"]),
            "familia": "CD_DI",
            "mayor": random.choice(["RES_MAY", "SAD"]),
            "insercion": random.choice(["CEE", "EMP"]),
        }[colectivo]
        ServicioContratado.objects.create(
            persona=persona,
            centro=centro,
            servicio=servicios[servicio_codigo],
            corresponsable=corresponsable,
            inicio_at=inicio,
        )

    def _anadir_contacto(self, persona):
        contacto = PersonaContacto.objects.create(
            nombre=fake.first_name(),
            apellido_1=persona.apellido_1,
            apellido_2=fake.last_name(),
            telefono=fake.phone_number(),
            email=fake.email(),
            consentimiento_comunicacion=True,
            fecha_consentimiento=date.today() - timedelta(days=random.randint(30, 730)),
        )
        VinculoPersonaContacto.objects.create(
            persona=persona,
            contacto=contacto,
            relacion=random.choice(["madre", "padre", "hermano", "hijo", "tutor"]),
            es_referencia_principal=True,
            es_emergencia=True,
        )
        if persona.medida_apoyo.tipo != "sin_medida":
            FiguraDeApoyo.objects.create(
                medida=persona.medida_apoyo,
                contacto=contacto,
                ambito="Representación en decisiones de salud y económicas relevantes.",
            )
        if random.random() < 0.3:
            NucleoFamiliar.objects.create(
                nombre_referencia=f"Familia {persona.apellido_1} {persona.apellido_2}",
                persona_referencia=contacto,
            ).personas_atendidas.add(persona)

    def _generar_plan_vida(self, persona):
        """Crea un Plan de Vida 2026 vigente con los 5 documentos del protocolo,
        4-6 objetivos repartidos por ámbitos, y reflejando voluntad de la persona
        sobre paneles visuales."""
        fecha_elab = date.today() - timedelta(days=random.randint(60, 270))
        plan = PlanDeVida.objects.create(
            persona=persona,
            anualidad=2026,
            estado=PlanDeVida.Estado.VIGENTE,
            gestor_caso=persona.gestor_caso,
            persona_referencia=persona.persona_referencia,
            fecha_elaboracion=fecha_elab,
            fecha_revision=fecha_elab,
            fecha_proxima_revision=fecha_elab + timedelta(days=365),
            firmado_persona_at=timezone.make_aware(datetime.combine(fecha_elab, time(10, 0))),
            firmado_apoyo_at=(
                timezone.make_aware(datetime.combine(fecha_elab, time(10, 15)))
                if persona.medida_apoyo.tipo != MedidaDeApoyo.Tipo.SIN_MEDIDA else None
            ),
            visible_en_paneles=random.random() < 0.4,
        )

        # Los 5 documentos del protocolo
        for tipo in DocumentoPlanDeVida.Tipo.values:
            estado = random.choices(
                [
                    DocumentoPlanDeVida.Estado.COMPLETADO,
                    DocumentoPlanDeVida.Estado.EN_ELABORACION,
                    DocumentoPlanDeVida.Estado.PENDIENTE,
                ],
                weights=[7, 2, 1],
            )[0]
            DocumentoPlanDeVida.objects.create(
                plan_vida=plan,
                tipo=tipo,
                estado=estado,
                fecha_completado=fecha_elab if estado == DocumentoPlanDeVida.Estado.COMPLETADO else None,
                # Los dos documentos finales del protocolo van a REPRISS (a través de Dirección)
                publicado_en_repriss=(
                    estado == DocumentoPlanDeVida.Estado.COMPLETADO
                    and tipo in (DocumentoPlanDeVida.Tipo.PROYECTO_VIDA, DocumentoPlanDeVida.Tipo.PLAN_APOYO)
                ),
                url_almacenamiento=f"https://aspaniasburgos.sharepoint.com/sites/PlanesVida/2026/{persona.codigo_interno}/{tipo}.docx" if estado != DocumentoPlanDeVida.Estado.PENDIENTE else "",
            )

        # Documentos 1, 2, 4, 5 del Plan de Vida (cabecera registrada;
        # contenido narrativo se rellena en _generar_documentos_plan_vida)
        self._generar_documentos_plan_vida(plan)

        # Objetivos del plan
        seleccion = random.sample(OBJETIVOS_DEMO, k=random.randint(4, 6))
        for ambito, descripcion, indicador, apoyos, prioridad in seleccion:
            obj = Objetivo.objects.create(
                plan_vida=plan,
                ambito=ambito,
                descripcion=descripcion,
                indicador_logro=indicador,
                apoyos_necesarios=apoyos,
                prioridad=prioridad,
                visible_en_panel=plan.visible_en_paneles and random.random() < 0.5,
                estado=random.choices(
                    [Objetivo.Estado.PROPUESTO, Objetivo.Estado.ACTIVO, Objetivo.Estado.LOGRADO, Objetivo.Estado.MANTENIMIENTO],
                    weights=[1, 5, 2, 1],
                )[0],
            )
            self._generar_revisiones_objetivo(obj, fecha_elab)

    def _generar_revisiones_objetivo(self, obj, fecha_revision):
        """Crea revisiones narrativas anuales del objetivo (formato Excel real)."""
        plan = obj.plan_vida
        responsable = plan.persona_referencia or plan.gestor_caso

        logrados = {
            Objetivo.Estado.LOGRADO: [
                "La persona ha alcanzado el objetivo en su totalidad. Se observa autonomía sostenida y satisfacción al hablar de ello.",
                "Hito completado dentro del plazo previsto. La persona muestra confianza y pide ya un nuevo reto vinculado.",
            ],
            Objetivo.Estado.ACTIVO: [
                "Avance moderado pero estable. Hace la tarea con supervisión cada vez menor.",
                "Progreso visible las últimas semanas. Quedan pasos por consolidar antes de poder darlo por logrado.",
            ],
            Objetivo.Estado.MANTENIMIENTO: [
                "El logro se mantiene con apoyo puntual. Se sigue trabajando para que no haya retroceso.",
            ],
            Objetivo.Estado.PROPUESTO: [
                "Aún no se ha iniciado el trabajo formal sobre el objetivo. Pendiente de planificar primeras sesiones.",
            ],
            Objetivo.Estado.ABANDONADO: [
                "La persona no desea seguir trabajando en este objetivo en este momento.",
            ],
        }
        motivos = [
            "Aparición de un episodio de salud que ha pausado el trabajo durante varias semanas.",
            "Los apoyos previstos resultaron insuficientes para el grado de complejidad real de la tarea.",
            "Cambio de rutinas en el centro tras reorganización del equipo asistencial.",
            "La persona ha priorizado otros aspectos de su vida durante este ciclo.",
        ]
        propuestas = [
            "Reforzar el apoyo visual con pictogramas ARASAAC y ajustar plantilla de pasos.",
            "Incluir sesiones específicas con la TO una vez por semana durante el próximo trimestre.",
            "Implicar a la familia para acompañar la rutina los fines de semana en domicilio.",
            "Acompañamiento del/de la monitor/a durante las primeras 4 semanas hasta consolidar.",
            "Revisar la formulación del objetivo con la persona para asegurar que sigue siendo significativo.",
        ]

        que_ha_logrado = random.choice(logrados.get(obj.estado, logrados[Objetivo.Estado.ACTIVO]))
        motivo_text = ""
        propuesta_text = ""
        if obj.estado in (Objetivo.Estado.ACTIVO, Objetivo.Estado.PROPUESTO, Objetivo.Estado.ABANDONADO):
            motivo_text = random.choice(motivos)
            propuesta_text = random.choice(propuestas)

        RevisionObjetivo.objects.create(
            objetivo=obj,
            anualidad=plan.anualidad,
            fecha_revision=fecha_revision,
            que_ha_logrado=que_ha_logrado,
            motivo_no_consecucion=motivo_text,
            propuesta_apoyos=propuesta_text,
            realizada_por=responsable,
        )

    def _generar_cambios_significativos(self, persona):
        """Genera 0-2 cambios significativos recientes."""
        n = random.choices([0, 1, 2], weights=[6, 3, 1])[0]
        if n == 0:
            return
        plan = persona.planes_vida.filter(estado=PlanDeVida.Estado.VIGENTE).first()
        ambitos = random.sample(list(CambioSignificativo.Ambito.values), k=n)
        descripciones = {
            "salud": "Episodio agudo registrado, ajuste de medicación tras revisión médica.",
            "empleo": "Cambio de puesto en el CEE por reorganización del taller.",
            "centro_vivienda": "Traslado interno entre módulos por cambio de necesidades de apoyo.",
            "rutinas": "Modificación de la rutina de mañanas tras valoración funcional.",
            "relaciones": "Pérdida de vínculo familiar significativo en los últimos meses.",
            "participacion": "Reincorporación al club social tras periodo de retirada.",
            "otro": "Cambio significativo detectado por la persona de referencia.",
        }
        for ambito in ambitos:
            CambioSignificativo.objects.create(
                persona=persona,
                plan_vida=plan,
                ambito=ambito,
                descripcion=descripciones.get(ambito, descripciones["otro"]),
                fecha_deteccion=date.today() - timedelta(days=random.randint(5, 90)),
                detectado_por=persona.persona_referencia,
                requiere_actualizacion_plan=True,
                procesado=random.random() < 0.4,
            )

    def _generar_intervenciones(self, persona, tipos_inter):
        """Genera 5-12 intervenciones en los últimos 60 días, repartidas entre la
        persona de referencia, el/la gestor/a y otros profesionales del pool."""
        n = random.randint(5, 12)
        tipos = list(tipos_inter.values())
        objetivos_persona = list(
            Objetivo.objects.filter(plan_vida__persona=persona, plan_vida__estado=PlanDeVida.Estado.VIGENTE)
        )
        from personas.models import Profesional

        candidatos = [p for p in [persona.persona_referencia, persona.gestor_caso] if p]
        if not candidatos:
            prof_disponible = Profesional.objects.first()
            if prof_disponible:
                candidatos = [prof_disponible]
            else:
                return

        for _ in range(n):
            dias = random.randint(0, 60)
            hora = random.randint(8, 18)
            fecha_h = timezone.now() - timedelta(days=dias, hours=random.randint(0, 6))
            fecha_h = fecha_h.replace(hour=hora, minute=random.choice([0, 15, 30, 45]), second=0, microsecond=0)
            tipo = random.choice(tipos)
            obj_vinculado = random.choice(objetivos_persona) if objetivos_persona and random.random() < 0.4 else None
            Intervencion.objects.create(
                persona=persona,
                profesional=random.choice(candidatos),
                tipo=tipo,
                fecha_hora=fecha_h,
                descripcion=fake.paragraph(nb_sentences=random.randint(2, 4)),
                objetivo_vinculado=obj_vinculado,
                confidencialidad=random.choices(
                    ["normal", "rest_clinica", "rest_juridica"],
                    weights=[7, 2, 1],
                )[0],
            )

    def _generar_citas(self, persona):
        """Genera 2-4 citas en la semana actual."""
        from personas.models import Profesional

        prof = persona.persona_referencia or persona.gestor_caso or Profesional.objects.first()
        if not prof:
            return
        hoy = timezone.localdate()
        inicio_semana = hoy - timedelta(days=hoy.weekday())
        for _ in range(random.randint(2, 4)):
            offset_dia = random.randint(0, 4)
            hora = random.choice([9, 10, 11, 12, 16, 17])
            dia = inicio_semana + timedelta(days=offset_dia)
            inicio = timezone.make_aware(datetime.combine(dia, time(hora, 0)))
            fin = inicio + timedelta(minutes=random.choice([30, 45, 60]))
            cita = Cita.objects.create(
                persona=persona,
                tipo=random.choices(
                    list(Cita.Tipo.values),
                    weights=[6, 2, 1, 1],
                )[0],
                inicio=inicio,
                fin=fin,
                ubicacion=persona.centro_referencia.nombre,
                estado=Cita.Estado.CONFIRMADA,
                notificada_a_familia=random.random() < 0.7,
            )
            cita.profesionales.add(prof)

    # ------------------------------------------------------------------
    # Documentos 1, 2, 4, 5 del Plan de Vida — contenedores vacíos.
    # Las preguntas/secciones/columnas/bloques se incorporarán cuando llegue
    # la plantilla en blanco oficial y se valide con Dirección de Centros y
    # Servicios. No se rellenan contenidos sintéticos derivados de los
    # documentos personales recibidos.
    # ------------------------------------------------------------------

    def _generar_documentos_plan_vida(self, plan):
        gestor = plan.gestor_caso
        referencia = plan.persona_referencia
        facilitador = referencia or gestor

        # Documento 1 — Historia de Vida + 21 preguntas oficiales (vacías)
        historia = HistoriaDeVida.objects.create(
            plan_vida=plan,
            fecha_recogida=plan.fecha_elaboracion,
            facilitador=facilitador,
        )
        for idx, (codigo, pregunta) in enumerate(PREGUNTAS_HISTORIA_VIDA, start=1):
            RespuestaHistoriaVida.objects.create(
                historia=historia,
                pregunta_codigo=codigo,
                pregunta_texto=pregunta,
                respuesta_texto="",
                orden=idx,
            )

        # Documento 2 — Algo sobre mí: contenedor + 11 secciones vacías (plantilla oficial)
        algo = AlgoSobreMi.objects.create(
            plan_vida=plan,
            fecha_actualizacion=plan.fecha_elaboracion,
            actualizado_por=facilitador,
        )
        for idx, (codigo, titulo) in enumerate(SECCIONES_ALGO_SOBRE_MI, start=1):
            SeccionAlgoSobreMi.objects.create(
                documento=algo,
                codigo=codigo,
                titulo=titulo,
                contenido="",
                orden=idx,
            )

        # Documento 4 — Plan de Apoyo: contenedor + 1 entrada por objetivo, sin rellenar
        plan_apoyo = PlanDeApoyo.objects.create(
            plan_vida=plan,
            fecha_realizacion=plan.fecha_elaboracion,
            realizado_por=gestor,
        )
        for idx, obj in enumerate(plan.objetivos.all(), start=1):
            EntradaPlanApoyo.objects.create(
                plan_apoyo=plan_apoyo,
                objetivo_vinculado=obj,
                titulo_objetivo=obj.descripcion,
                orden=idx,
            )

        # Documento 5 — Proyecto de Vida: contenedor vacío con publicación REPRISS
        ProyectoDeVida.objects.create(
            plan_vida=plan,
            fecha=plan.fecha_elaboracion,
            elaborado_por=gestor,
            publicado_en_repriss=(plan.estado == PlanDeVida.Estado.VIGENTE),
        )
