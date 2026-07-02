"""Genera un snapshot de los KPIs de Planes de Vida.

Uso:
    python manage.py generar_snapshot_planes_vida [--etiqueta "Cierre 2026Q2"]

Idempotente: si ya existe un snapshot para hoy lo sobreescribe.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from indicadores.calc import kpis_planes_vida
from indicadores.models import SnapshotPlanesVida


class Command(BaseCommand):
    help = "Calcula y guarda un snapshot de los KPIs de Planes de Vida."

    def add_arguments(self, parser):
        parser.add_argument("--etiqueta", type=str, default="", help="Etiqueta libre.")

    def handle(self, *args, **opts):
        data = kpis_planes_vida()
        hoy = timezone.localdate()

        desglose = {
            c["centro"].codigo: {
                "nombre": c["centro"].nombre,
                "personas": c["personas"],
                "realizados": c["realizados"],
                "pendientes": c["pendientes"],
                "revisados": c["revisados"],
                "fuera_plazo": c["fuera_plazo"],
            }
            for c in data["desglose_centros"]
        }

        snapshot, creado = SnapshotPlanesVida.objects.update_or_create(
            fecha=hoy,
            defaults={
                "etiqueta": opts["etiqueta"],
                "total_usuarios": data["total_usuarios"],
                "usuarios_fab": data["usuarios_fab"],
                "usuarios_aspaniasmerc": data["usuarios_aspaniasmerc"],
                "pv_realizados": data["realizados"]["total"],
                "pv_pendientes": data["pendientes_realizar"]["total"],
                "pv_revisados": data["revisados"]["total"],
                "pv_fuera_plazo": data["fuera_plazo"]["total"],
                "desglose_centros": desglose,
            },
        )
        accion = "creado" if creado else "actualizado"
        self.stdout.write(self.style.SUCCESS(
            f"Snapshot {accion}: {snapshot.fecha} · {snapshot.total_usuarios} usuarios · "
            f"{snapshot.pv_realizados} PV realizados · {snapshot.pv_fuera_plazo} fuera de plazo"
        ))
