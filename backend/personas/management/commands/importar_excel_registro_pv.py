"""Importador del Excel 'Registro PV por servicios. Global Grupo Aspanias.xlsx'.

Carga personas, profesionales y planes de vida desde las 13 hojas de centro
del Excel real (o su versión _PSEUDO.xlsx).

Uso:
    python manage.py importar_excel_registro_pv ruta/al/archivo.xlsx --anualidad 2026 [--dry-run]

Asume estructura:
- Fila 7: cabecera de tabla (Usuario/a | Gestor/a de caso | Persona de referencia |
  PV realizado | PV revisado | ¿Está en Teams? | ¿Está en Repriss? |
  Fecha prevista realización PV | Fecha revisión PV | Estado revisión |
  Usuario/a compartido con residencia /vivienda)
- Fila 8 en adelante: datos

Crea/actualiza:
- Centro (si no existe, lo crea con su corresponsable según mapeo).
- Profesional (gestores y personas de referencia, identificados por nombre).
- PersonaAtendida (con código autogenerado si no encuentra coincidencia por nombre).
- PlanDeVida con flags pv_realizado, pv_revisado, estado_revision y fechas.
"""
import re
from datetime import date, datetime
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from personas.models import Centro, PersonaAtendida, Profesional
from pia.models import PlanDeVida

# Mapeo hoja → (codigo_centro, nombre_centro_canonico, corresponsable, municipio)
MAPEO_CENTROS = {
    "Res. Quint.": ("RES_QUINT", "Residencia y UA Quintanadueñas",
                    "fundacion_aspanias_burgos", "Quintanadueñas"),
    "CD Quint.": ("CD_QUINT", "Centro Ocupacional Quintanadueñas",
                  "fundacion_aspanias_burgos", "Quintanadueñas"),
    "Vicente Aleixandre": ("VICENTE", "Centro Multiactividad Vicente Aleixandre",
                           "fundacion_aspanias_burgos", "Burgos"),
    "Puentesauco": ("RES_PUENTESAUCO", "Residencia Puentesauco (RHP)",
                    "aspaniasmerc", "Burgos"),
    "Salas": ("SAL", "Residencia y Centro de Día Salas",
              "aspaniasmerc", "Salas de los Infantes"),
    "Fuentecillas": ("FUE", "Centro Mayores Fuentecillas",
                     "fundacion_aspanias_burgos", "Burgos"),
    "Puentes": ("PUENTES", "Servicio de Vida Independiente",
                "fundacion_aspanias_burgos", "Burgos"),
    "CD Puentesauco": ("CD_PUENTESAUCO", "Centro Ocupacional Puentesauco",
                       "aspaniasmerc", "Burgos"),
    "Río Arlanza": ("LAR", "Residencia Río Arlanza",
                    "fundacion_aspanias_burgos", "Lara"),
    "Santa Mª": ("SANTA_M", "Residencia Santa María",
                 "fundacion_aspanias_burgos", "Burgos"),
    "Viviendas Puentesauco": ("VIV_PUENTESAUCO", "Viviendas Puentesauco",
                              "aspaniasmerc", "Burgos"),
    "Viviendas Asociación": ("VIV_ASOC", "Viviendas Asociación",
                             "fundacion_aspanias_burgos", "Burgos"),
    "Viviendas Fuentecillas": ("VIV_FUE", "Viviendas Fuentecillas",
                               "fundacion_aspanias_burgos", "Burgos"),
}

CABECERAS = {
    "usuario/a": "usuario",
    "gestor/a de caso": "gestor",
    "persona de referencia": "referencia",
    "pv realizado": "pv_realizado",
    "pv revisado": "pv_revisado",
    "¿está en teams?": "en_teams",
    "está en teams?": "en_teams",
    "esta en teams?": "en_teams",
    "¿está en repriss?": "en_repriss",
    "está en repriss?": "en_repriss",
    "esta en repriss?": "en_repriss",
    "fecha prevista realización pv": "fecha_prevista",
    "fecha prevista realizacion pv": "fecha_prevista",
    "fecha revisión pv": "fecha_revision",
    "fecha revision pv": "fecha_revision",
    "estado revisión": "estado_revision",
    "estado revision": "estado_revision",
    "usuario/a compartido con residencia /vivienda": "compartido",
    "usuario/a compartido con residencia /viv": "compartido",
}


def _norm(s):
    if not isinstance(s, str):
        return ""
    return s.strip().lower()


def _bool_si_no(v):
    if v is None:
        return False
    s = str(v).strip().upper()
    return s in ("SI", "SÍ", "TRUE", "1", "X")


def _parse_fecha(v):
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v.date()
    if isinstance(v, date):
        return v
    s = str(v).strip()
    for fmt in ("%d/%m/%Y", "%Y-%m-%d", "%d-%m-%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def _parse_estado_revision(v):
    if v is None:
        return "pendiente"
    s = str(v).strip().lower()
    if "fuera" in s:
        return "fuera_plazo"
    if "en plazo" in s or "plazo" in s:
        return "en_plazo"
    return "pendiente"


class Command(BaseCommand):
    help = "Importa el Excel 'Registro PV por servicios' del Grupo Aspanias."

    def add_arguments(self, parser):
        parser.add_argument("ruta_excel", type=str, help="Ruta absoluta al .xlsx.")
        parser.add_argument("--anualidad", type=int, required=True, help="Año del Plan (2025, 2026...).")
        parser.add_argument("--dry-run", action="store_true", help="No escribe en BD; reporta lo que haría.")

    @transaction.atomic
    def handle(self, *args, **opts):
        try:
            from openpyxl import load_workbook
        except ImportError:
            raise CommandError("Falta openpyxl. pip install openpyxl")

        ruta = Path(opts["ruta_excel"])
        if not ruta.exists():
            raise CommandError(f"No existe el archivo: {ruta}")

        wb = load_workbook(ruta, data_only=True)
        anualidad = opts["anualidad"]
        dry = opts["dry_run"]

        resumen = {
            "centros_creados": 0, "centros_existentes": 0,
            "personas_creadas": 0, "personas_actualizadas": 0,
            "profesionales_creados": 0,
            "planes_creados": 0, "planes_actualizados": 0,
            "errores": [],
        }

        if dry:
            self.stdout.write(self.style.NOTICE("=== DRY-RUN — no se modifica BD ==="))

        for hoja in MAPEO_CENTROS:
            if hoja not in wb.sheetnames:
                resumen["errores"].append(f"Hoja '{hoja}' no encontrada en el Excel.")
                continue
            try:
                self._procesar_hoja(wb[hoja], hoja, anualidad, resumen)
            except Exception as exc:
                resumen["errores"].append(f"[{hoja}] {exc}")

        if dry:
            transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"\nImportación {'(simulada) ' if dry else ''}finalizada."
        ))
        for k, v in resumen.items():
            if k != "errores":
                self.stdout.write(f"  {k}: {v}")
        if resumen["errores"]:
            self.stdout.write(self.style.WARNING(f"  errores: {len(resumen['errores'])}"))
            for err in resumen["errores"][:15]:
                self.stdout.write(self.style.ERROR(f"    · {err}"))

    def _procesar_hoja(self, ws, nombre_hoja, anualidad, resumen):
        codigo, nombre_canonico, corresponsable, municipio = MAPEO_CENTROS[nombre_hoja]

        # Crear/recuperar Centro
        centro, creado = Centro.objects.get_or_create(
            codigo=codigo,
            defaults={"nombre": nombre_canonico, "corresponsable": corresponsable,
                      "municipio": municipio, "activo": True},
        )
        resumen["centros_creados" if creado else "centros_existentes"] += 1

        # Localizar fila de cabecera
        fila_cab = None
        for r_idx in range(1, 15):
            row_vals = [_norm(c) for c in (cell.value for cell in ws[r_idx])]
            if "usuario/a" in row_vals:
                fila_cab = r_idx
                break
        if not fila_cab:
            resumen["errores"].append(f"[{nombre_hoja}] no encuentro fila de cabecera con 'Usuario/a'.")
            return

        # Indexar columnas
        col_idx = {}
        for c_idx, cell in enumerate(ws[fila_cab], start=1):
            clave = CABECERAS.get(_norm(cell.value))
            if clave:
                col_idx[clave] = c_idx

        if "usuario" not in col_idx:
            resumen["errores"].append(f"[{nombre_hoja}] cabecera 'Usuario/a' no localizada.")
            return

        # Procesar filas
        for row in ws.iter_rows(min_row=fila_cab + 1, values_only=False):
            def val(clave):
                idx = col_idx.get(clave)
                if idx is None or idx - 1 >= len(row):
                    return None
                return row[idx - 1].value

            nombre_usuario = val("usuario")
            if not nombre_usuario or not isinstance(nombre_usuario, str) or not nombre_usuario.strip():
                continue

            persona = self._get_or_create_persona(nombre_usuario.strip(), centro, corresponsable, resumen)
            if persona is None:
                continue

            gestor = self._get_or_create_profesional(val("gestor"), resumen, es_gestor=True)
            referencia = self._get_or_create_profesional(val("referencia"), resumen, es_gestor=False)

            # Actualizar persona con sus profesionales si cambian
            cambios = []
            if gestor and persona.gestor_caso_id != gestor.id:
                persona.gestor_caso = gestor
                cambios.append("gestor")
            if referencia and persona.persona_referencia_id != referencia.id:
                persona.persona_referencia = referencia
                cambios.append("referencia")
            if cambios:
                persona.save()

            # Crear/actualizar PlanDeVida
            plan, creado = PlanDeVida.objects.update_or_create(
                persona=persona,
                anualidad=anualidad,
                defaults={
                    "gestor_caso": gestor,
                    "persona_referencia": referencia,
                    "pv_realizado": _bool_si_no(val("pv_realizado")),
                    "pv_revisado": _bool_si_no(val("pv_revisado")),
                    "fecha_prevista_realizacion": _parse_fecha(val("fecha_prevista")),
                    "fecha_revision": _parse_fecha(val("fecha_revision")),
                    "estado_revision": _parse_estado_revision(val("estado_revision")),
                    "compartido_con_residencia_vivienda": _bool_si_no(val("compartido")),
                    "estado": PlanDeVida.Estado.VIGENTE,
                },
            )
            resumen["planes_creados" if creado else "planes_actualizados"] += 1

    def _get_or_create_persona(self, nombre_completo, centro, corresponsable, resumen):
        """Busca persona por nombre. Si no existe, la crea con código autogenerado."""
        partes = nombre_completo.split()
        if len(partes) < 2:
            resumen["errores"].append(f"Nombre incompleto: '{nombre_completo}'")
            return None
        # Heurística: 'Mª ÁNGELES ANDRÉS CHAPERO' → nombre 'Mª ÁNGELES', apellidos 'ANDRÉS CHAPERO'
        # Para no inventar, asumo: nombre = primera palabra, apellido_1 = segunda, apellido_2 = resto
        nombre = partes[0]
        apellido_1 = partes[1] if len(partes) > 1 else ""
        apellido_2 = " ".join(partes[2:]) if len(partes) > 2 else ""

        # Buscar persona existente por nombre completo similar
        existing = PersonaAtendida.objects.filter(
            nombre__iexact=nombre,
            apellido_1__iexact=apellido_1,
        ).first()
        if existing:
            return existing

        # Crear nueva con código autogenerado
        anio = datetime.now().year
        prefijo = f"{centro.codigo}-{anio}-"
        siguiente = PersonaAtendida.objects.filter(codigo_interno__startswith=prefijo).count() + 1
        codigo = f"{prefijo}{siguiente:05d}"

        persona = PersonaAtendida.objects.create(
            codigo_interno=codigo,
            nombre=nombre,
            apellido_1=apellido_1,
            apellido_2=apellido_2,
            fecha_nacimiento=date(1970, 1, 1),  # placeholder; se completa después
            corresponsable_principal=corresponsable,
            centro_referencia=centro,
            fecha_alta=date.today(),
        )
        resumen["personas_creadas"] += 1
        # MedidaDeApoyo obligatoria — crear con "sin_medida" por defecto, a ajustar después
        from personas.models import MedidaDeApoyo
        MedidaDeApoyo.objects.get_or_create(
            persona=persona,
            defaults={"tipo": MedidaDeApoyo.Tipo.SIN_MEDIDA, "vigente": True},
        )
        return persona

    def _get_or_create_profesional(self, nombre_completo, resumen, es_gestor=False):
        if not nombre_completo or not isinstance(nombre_completo, str) or not nombre_completo.strip():
            return None
        nombre_completo = nombre_completo.strip()
        # Buscar por nombre_completo exacto
        prof = Profesional.objects.filter(nombre_completo__iexact=nombre_completo).first()
        if prof:
            if es_gestor and not prof.puede_ser_gestor_caso:
                prof.puede_ser_gestor_caso = True
                prof.save(update_fields=["puede_ser_gestor_caso"])
            return prof

        # Crear nuevo (necesita un auth.User vinculado y email único)
        # Generar slug de email a partir del nombre
        slug = re.sub(r"[^a-z0-9]+", ".", nombre_completo.lower().strip()).strip(".")
        email = f"{slug}@aspaniasburgos.com"
        # Asegurar unicidad
        counter = 1
        User = get_user_model()
        username_base = slug[:30]
        username = username_base
        while User.objects.filter(username=username).exists():
            username = f"{username_base}_{counter}"
            counter += 1
        # Asegurar unicidad de email
        while Profesional.objects.filter(email_m365=email).exists():
            email = f"{slug}.{counter}@aspaniasburgos.com"
            counter += 1
        user = User.objects.create_user(username=username, email=email)

        prof = Profesional.objects.create(
            user=user,
            nombre_completo=nombre_completo,
            email_m365=email,
            puede_ser_gestor_caso=es_gestor,
            activo=True,
        )
        resumen["profesionales_creados"] += 1
        return prof
