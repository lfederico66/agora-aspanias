"""Trigger PostgreSQL para bitácora append-only — Fase 2.5.2.

Garantiza a nivel BD que ningún DELETE prospere sobre core_registroacceso, ni
siquiera el de un superuser que se conecte directamente con psql. Es una capa
de defensa adicional al ORM.

La eliminación masiva por política de retención (>= 24 meses) se hace en
producción mediante un job documentado que desactiva temporalmente el trigger
con un usuario de mantenimiento ``agora_maintenance`` dedicado.

Solo se aplica si el backend es PostgreSQL — en otros engines la migración
es no-op y los tests siguen funcionando.
"""
from django.db import migrations


CREAR_TRIGGER_SQL = """
CREATE OR REPLACE FUNCTION agora_impedir_borrado_registro_acceso()
RETURNS TRIGGER AS $$
BEGIN
    RAISE EXCEPTION
        'No se pueden borrar entradas de la bitácora directamente. '
        'Usar el job documentado de aplicación de política de retención (>= 24 meses). '
        'RGPD art. 32 — trazabilidad append-only.'
        USING ERRCODE = 'P0001';
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_bitacora_append_only
    ON core_registroacceso;

CREATE TRIGGER trigger_bitacora_append_only
    BEFORE DELETE ON core_registroacceso
    FOR EACH ROW
    EXECUTE FUNCTION agora_impedir_borrado_registro_acceso();
"""

ELIMINAR_TRIGGER_SQL = """
DROP TRIGGER IF EXISTS trigger_bitacora_append_only ON core_registroacceso;
DROP FUNCTION IF EXISTS agora_impedir_borrado_registro_acceso();
"""


def aplicar_si_postgres(apps, schema_editor):
    """Solo aplica el trigger en PostgreSQL. En SQLite (tests) es no-op."""
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(CREAR_TRIGGER_SQL)


def revertir_si_postgres(apps, schema_editor):
    if schema_editor.connection.vendor != "postgresql":
        return
    schema_editor.execute(ELIMINAR_TRIGGER_SQL)


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(aplicar_si_postgres, revertir_si_postgres),
    ]
