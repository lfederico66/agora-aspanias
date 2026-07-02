"""Importador del Excel legado de seguimiento de Planes de Vida.

Lee el Excel compartido que actualmente usan los gestores/as de caso (sección 7
del protocolo: centros, gestores/as, estado del plan, fecha de revisión, alertas)
y crea/actualiza `PlanDeVida` en ÁGORA para la anualidad indicada.

Uso:
    python manage.py importar_excel_planes_vida ruta/al/excel.xlsx --anualidad 2026 [--dry-run]

Estado: esqueleto v0.1 — ajustar nombres de columnas exactos cuando se reciba
el Excel real. Comprueba conflictos y reporta un resumen sin tocar BD si se
ejecuta con --dry-run.

ATENCIÓN RGPD: el Excel puede contener datos reales. NO subir copias al repo.
Procesar siempre desde una ruta local fuera del repositorio.
"""
from datetime import date, datetime
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from personas.models import PersonaAtendida, Profesional
from pia.models import DocumentoPlanDeVida, PlanDeVida

COLUMNAS_ESPERADAS = {
    # Columna en Excel → atributo ÁGORA
    # Ajustar exactamente al fichero real antes de uso en producción.
    "codigo_persona": "codigo_interno",   # Código humano de la persona (ej. FUE-2024-00012)
    "centro": "centro_codigo",            # Código del centro (FUE, LAR, SAL, VIL, CEE)
    "gestor_email": "gestor_email",       # Email M365 del gestor/a de caso
    "referencia_email": "referencia_email",
    "estado": "estado_plan",              # vigente / en_revision / archivado / elaboracion
    "fecha_revision": "fecha_revision",   # dd/mm/aaaa
    "proxima_revision": "fecha_proxima_revision",
    "alerta": "alerta_renovacion",        # texto libre
    "doc_historia_vida": "doc_historia_vida",   # URL en Teams/OneDrive
    "doc_algo_sobre_mi": "doc_algo_sobre_mi",
    "doc_revision_objetivos": "doc_revision_objetivos",
    "doc_plan_apoyo": "doc_plan_apoyo",
    "doc_proyecto_vida": "doc_proyecto_vida",
}

ESTADO_MAP = {
    "vigente": PlanDeVida.Estado.VIGENTE,
    "en revisión": PlanDeVida.Estado.EN_REVISION,
    "en revision": PlanDeVida.Estado.EN_REVISION,
    "en elaboración": PlanDeVida.Estado.EN_ELABORACION,
    "en elaboracion": PlanDeVida.Estado.EN_ELABORACION,
    "archivado": PlanDeVida.Estado.ARCHIVADO,
}

DOC_FIELD_MAP = {
    "doc_historia_vida": DocumentoPlanDeVida.Tipo.HISTORIA_VIDA,
    "doc_algo_sobre_mi": DocumentoPlanDeVida.Tipo.ALGO_SOBRE_MI,
    "doc_revision_objetivos": DocumentoPlanDeVida.Tipo.REVISION_OBJETIVOS,
    "doc_plan_apoyo": DocumentoPlanDeVida.Tipo.PLAN_APOYO,
    "doc_proyecto_vida": DocumentoPlanDeVida.Tipo.PROYECTO_VIDA,
}


class Command(BaseCommand):
    help = "Importa el Excel legado de seguimiento de Planes de Vida a ÁGORA."

    def add_arguments(self, parser):
        parser.add_argument("ruta_excel", type=str, nargs="?", help="Ruta absoluta al .xlsx legado (omitir si se usa --generar-plantilla).")
        parser.add_argument("--anualidad", type=int, help="Año del Plan (2025, 2026...). Requerido para importar.")
        parser.add_argument("--dry-run", action="store_true", help="No escribe en BD; reporta lo que haría.")
        parser.add_argument("--hoja", type=str, default=None, help="Nombre de la hoja a leer (por defecto la primera).")
        parser.add_argument(
            "--generar-plantilla", type=str, default=None,
            help="Ruta donde escribir un .xlsx EN BLANCO con las cabeceras esperadas (no requiere ruta_excel).",
        )

    def handle(self, *args, **opts):
        # Modo: generar plantilla vacía y salir
        if opts["generar_plantilla"]:
            self._generar_plantilla(Path(opts["generar_plantilla"]))
            return

        if not opts["ruta_excel"]:
            raise CommandError("Falta `ruta_excel`. Usa --generar-plantilla para crear una plantilla en blanco primero.")
        if not opts["anualidad"]:
            raise CommandError("Falta --anualidad para importar.")

        ruta = Path(opts["ruta_excel"])
        if not ruta.exists():
            raise CommandError(f"No existe el archivo: {ruta}")

        try:
            import openpyxl  # noqa: F401
        except ImportError:
            raise CommandError(
                "Falta openpyxl. Añade 'openpyxl' a requirements.txt y reinstala dependencias."
            )

        from openpyxl import load_workbook
        wb = load_workbook(ruta, data_only=True)
        ws = wb[opts["hoja"]] if opts["hoja"] else wb.active

        # Cabeceras: fila 1
        cabeceras = {cell.value: idx for idx, cell in enumerate(ws[1])}
        faltantes = [c for c in COLUMNAS_ESPERADAS if c not in cabeceras]
        if faltantes:
            self.stdout.write(self.style.WARNING(
                f"Columnas faltantes en el Excel ({faltantes}). Continúo con las disponibles."
            ))

        resumen = {"creados": 0, "actualizados": 0, "sin_persona": 0, "errores": []}
        anualidad = opts["anualidad"]
        dry = opts["dry_run"]

        if dry:
            self.stdout.write(self.style.NOTICE("DRY-RUN — no se modifica BD."))

        with transaction.atomic():
            for row in ws.iter_rows(min_row=2, values_only=True):
                try:
                    self._procesar_fila(row, cabeceras, anualidad, resumen, dry)
                except Exception as exc:
                    resumen["errores"].append(str(exc))

            if dry:
                transaction.set_rollback(True)

        self.stdout.write(self.style.SUCCESS(
            f"Importación {'(simulada) ' if dry else ''}finalizada. "
            f"Creados: {resumen['creados']} · Actualizados: {resumen['actualizados']} · "
            f"Sin persona: {resumen['sin_persona']} · Errores: {len(resumen['errores'])}."
        ))
        for err in resumen["errores"][:10]:
            self.stdout.write(self.style.ERROR(f"  · {err}"))

    def _procesar_fila(self, row, cabeceras, anualidad, resumen, dry):
        def col(nombre):
            idx = cabeceras.get(nombre)
            return row[idx] if idx is not None and idx < len(row) else None

        codigo_persona = col("codigo_persona")
        if not codigo_persona:
            return

        try:
            persona = PersonaAtendida.objects.get(codigo_interno=str(codigo_persona).strip())
        except PersonaAtendida.DoesNotExist:
            resumen["sin_persona"] += 1
            return

        gestor = self._buscar_profesional(col("gestor_email"))
        referencia = self._buscar_profesional(col("referencia_email"))

        plan, creado = PlanDeVida.objects.update_or_create(
            persona=persona,
            anualidad=anualidad,
            defaults={
                "estado": ESTADO_MAP.get(str(col("estado") or "").strip().lower(), PlanDeVida.Estado.EN_ELABORACION),
                "gestor_caso": gestor,
                "persona_referencia": referencia,
                "fecha_revision": self._parsear_fecha(col("fecha_revision")),
                "fecha_proxima_revision": self._parsear_fecha(col("proxima_revision")),
                "notas": str(col("alerta") or ""),
            },
        )
        resumen["creados" if creado else "actualizados"] += 1

        # Documentos cuyas URLs vengan rellenas
        for col_excel, tipo_doc in DOC_FIELD_MAP.items():
            url = col(col_excel)
            if not url:
                continue
            DocumentoPlanDeVida.objects.update_or_create(
                plan_vida=plan, tipo=tipo_doc,
                defaults={
                    "estado": DocumentoPlanDeVida.Estado.COMPLETADO,
                    "url_almacenamiento": str(url),
                    "publicado_en_repriss": tipo_doc in (
                        DocumentoPlanDeVida.Tipo.PROYECTO_VIDA,
                        DocumentoPlanDeVida.Tipo.PLAN_APOYO,
                    ),
                },
            )

    def _buscar_profesional(self, email):
        if not email:
            return None
        return Profesional.objects.filter(email_m365__iexact=str(email).strip()).first()

    def _parsear_fecha(self, valor):
        if valor is None or valor == "":
            return None
        if isinstance(valor, datetime):
            return valor.date()
        if isinstance(valor, date):
            return valor
        try:
            return datetime.strptime(str(valor).strip(), "%d/%m/%Y").date()
        except ValueError:
            try:
                return datetime.strptime(str(valor).strip(), "%Y-%m-%d").date()
            except ValueError:
                return None

    def _generar_plantilla(self, ruta: Path):
        """Genera un .xlsx en blanco con las cabeceras esperadas + 1 fila de ejemplo comentada."""
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Alignment, Font, PatternFill
        except ImportError:
            raise CommandError("Falta openpyxl en el entorno.")

        if ruta.exists():
            raise CommandError(f"Ya existe un archivo en {ruta}. Borra o cambia la ruta.")
        if ruta.suffix.lower() != ".xlsx":
            ruta = ruta.with_suffix(".xlsx")

        wb = Workbook()
        ws = wb.active
        ws.title = "Seguimiento"

        cabeceras = list(COLUMNAS_ESPERADAS.keys())
        ws.append(cabeceras)

        # Estilo de cabecera
        header_fill = PatternFill(start_color="1E6B4B", end_color="1E6B4B", fill_type="solid")
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF")
            cell.fill = header_fill
            cell.alignment = Alignment(horizontal="center", vertical="center")

        # Fila de ejemplo (vacía con comentarios en valor de ejemplo)
        ejemplo = [
            "FUE-2026-00001",        # codigo_persona
            "FUE",                    # centro
            "gestora@aspaniasburgos.com",
            "referencia@aspaniasburgos.com",
            "vigente",                # estado
            "15/01/2026",             # fecha_revision
            "15/01/2027",             # proxima_revision
            "Renovación pendiente para enero 2027",  # alerta
            "https://teams.../HistoriaVida.docx",
            "https://teams.../AlgoSobreMi.docx",
            "https://teams.../RevisionObjetivos.xlsx",
            "https://teams.../PlanApoyo.xlsx",
            "https://teams.../ProyectoVida.docx",
        ]
        ws.append(ejemplo)
        for cell in ws[2]:
            cell.font = Font(italic=True, color="999999")

        # Ajustar anchos de columna
        anchos = {
            "codigo_persona": 18, "centro": 8, "gestor_email": 30, "referencia_email": 30,
            "estado": 14, "fecha_revision": 14, "proxima_revision": 14, "alerta": 40,
            "doc_historia_vida": 40, "doc_algo_sobre_mi": 40, "doc_revision_objetivos": 40,
            "doc_plan_apoyo": 40, "doc_proyecto_vida": 40,
        }
        for idx, key in enumerate(cabeceras, start=1):
            ws.column_dimensions[ws.cell(row=1, column=idx).column_letter].width = anchos.get(key, 20)

        # Hoja "Instrucciones"
        wi = wb.create_sheet("Instrucciones")
        wi.append(["Plantilla de importación de Planes de Vida — ÁGORA"])
        wi.append([])
        wi.append(["Columna", "Obligatoria", "Formato", "Descripción"])
        descripciones = [
            ("codigo_persona", "Sí", "FUE-2026-00001", "Código interno de la persona en ÁGORA."),
            ("centro", "Sí", "FUE/LAR/SAL/VIL/CEE", "Código corto del centro."),
            ("gestor_email", "Sí", "email", "Email M365 del Gestor/a de Caso (Protocolo §2.1)."),
            ("referencia_email", "Sí", "email", "Email M365 de la Persona de Referencia (Protocolo §2.2)."),
            ("estado", "Sí", "vigente/en_revision/...", "Estado actual del Plan de Vida."),
            ("fecha_revision", "No", "dd/mm/aaaa", "Fecha de última revisión."),
            ("proxima_revision", "No", "dd/mm/aaaa", "Fecha de próxima revisión anual."),
            ("alerta", "No", "texto libre", "Alertas/observaciones de renovación."),
            ("doc_historia_vida", "No", "URL Teams/OneDrive", "Enlace al documento 1."),
            ("doc_algo_sobre_mi", "No", "URL Teams/OneDrive", "Enlace al documento 2."),
            ("doc_revision_objetivos", "No", "URL Teams/OneDrive", "Enlace al documento 3."),
            ("doc_plan_apoyo", "No", "URL Teams/OneDrive", "Enlace al documento 4."),
            ("doc_proyecto_vida", "No", "URL Teams/OneDrive", "Enlace al documento 5."),
        ]
        for fila in descripciones:
            wi.append(fila)
        wi.append([])
        wi.append(["Uso: borra la fila 2 de ejemplo y rellena tus datos. Después ejecuta:"])
        wi.append(["  python manage.py importar_excel_planes_vida ruta/al/archivo.xlsx --anualidad 2026 --dry-run"])
        wi.append(["  python manage.py importar_excel_planes_vida ruta/al/archivo.xlsx --anualidad 2026"])
        for cell in wi[3]:
            cell.font = Font(bold=True)
        wi.column_dimensions["A"].width = 28
        wi.column_dimensions["B"].width = 12
        wi.column_dimensions["C"].width = 24
        wi.column_dimensions["D"].width = 50

        wb.save(ruta)
        self.stdout.write(self.style.SUCCESS(f"Plantilla generada en: {ruta}"))
