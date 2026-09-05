"""
Comando de importación del censo de Fuentecillas al modelo real.

    python manage.py importar_fuentecillas <fichero.xlsx> [--dry-run] [--informe <salida.xlsx>]

Usa la capa pura `personas.importadores.fuentecillas` (normalización y
validación); aquí solo se persiste. Todo o nada (transacción): si una persona
falla al escribir, no se carga ninguna. Reejecutable: si el DNI ya existe, la
persona se OMITE (no se duplica ni se sobrescribe — las correcciones post-carga
se hacen en ÁGORA, no reimportando).
"""
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from personas.importadores import fuentecillas as imp
from personas.models import (
    Centro, EnfermedadCronica, PersonaAtendida, PerfilDI, PerfilMayor,
    PersonaContacto, VinculoPersonaContacto,
)


class Command(BaseCommand):
    help = "Importa el censo consolidado de Fuentecillas (pre-piloto)."

    def add_arguments(self, parser):
        parser.add_argument("fichero")
        parser.add_argument("--dry-run", action="store_true",
                            help="Valida y genera informe sin escribir nada.")
        parser.add_argument("--informe", default="informe_importacion_fuentecillas.xlsx")

    def handle(self, *args, **opts):
        ruta = Path(opts["fichero"])
        if not ruta.exists():
            raise CommandError(f"No existe el fichero: {ruta}")

        registros, excepciones, avisos = imp.procesar(ruta)
        imp.generar_informe(registros, excepciones, avisos, Path(opts["informe"]))
        self.stdout.write(f"Importables: {len(registros)} · Excepciones: {len(excepciones)}")
        self.stdout.write(f"Informe: {opts['informe']}")

        if opts["dry_run"]:
            self.stdout.write(self.style.SUCCESS("Dry-run: no se ha escrito nada."))
            return

        creadas = omitidas = 0
        with transaction.atomic():
            centros = {}
            for clave, datos in imp.CENTROS.items():
                centros[clave], _ = Centro.objects.get_or_create(
                    codigo=datos["codigo"],
                    defaults={"nombre": datos["nombre"],
                              "corresponsable": Centro.Corresponsable.FUNDACION,
                              "municipio": "Burgos"},
                )

            ultimo = (PersonaAtendida.objects.filter(codigo_interno__startswith="FUE-MIG-")
                      .count())
            for r in registros:
                p = r["persona"]
                if p["dni_nie"] and PersonaAtendida.objects.filter(dni_nie=p["dni_nie"]).exists():
                    omitidas += 1
                    continue
                ultimo += 1
                persona = PersonaAtendida.objects.create(
                    codigo_interno=f"FUE-MIG-{ultimo:05d}",
                    centro_referencia=centros[r["centro"]],
                    **p,
                )
                pm = r["perfil_mayor"]
                PerfilMayor.objects.create(persona=persona, **pm)
                if r["perfil_di"]:
                    PerfilDI.objects.create(persona=persona, **r["perfil_di"])
                for enf in r["enfermedades"]:
                    EnfermedadCronica.objects.create(
                        persona=persona, nombre=enf[:255],
                        fecha_diagnostico=r["f_validez_diag"],
                    )
                for diag in r["diagnosticos"]:
                    EnfermedadCronica.objects.get_or_create(
                        persona=persona, nombre=diag[:255],
                        defaults={"fecha_diagnostico": r["f_validez_diag"],
                                  "notas": "Diagnóstico principal/secundario (migrado)"},
                    )
                c = r["contacto"]
                if c:
                    contacto = PersonaContacto.objects.create(
                        nombre=c["nombre"][:64], movil=c["movil"],
                        telefono_fijo=c["telefono_fijo"], email=c["email"],
                        notas=(f"Forma de comunicación preferente: {c['forma_comunicacion']}. "
                               f"Parentesco (texto origen): {c['relacion_texto']}").strip(),
                    )
                    VinculoPersonaContacto.objects.create(
                        persona=persona, contacto=contacto, relacion=c["relacion"],
                        es_referencia_principal=True, es_emergencia=True,
                        orden_emergencia=1,
                    )
                creadas += 1

        self.stdout.write(self.style.SUCCESS(
            f"Cargadas: {creadas} · Omitidas (DNI ya existente): {omitidas} · "
            f"Excepciones sin cargar: {len(excepciones)}"))
