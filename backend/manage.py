#!/usr/bin/env python
"""Utilidad de línea de comandos de Django para ÁGORA."""
import os
import sys


def main():
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "agora.settings.dev")
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "No se puede importar Django. Comprueba que está instalado y "
            "que el entorno virtual está activado."
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()
