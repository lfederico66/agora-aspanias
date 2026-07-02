"""Campos de modelo con cifrado a nivel aplicación — Fase 2.5.1.

Diseñado para campos sensibles que NO necesitan ser indexables (NUSS, TSI...).
No se puede hacer ``filter(numero_tarjeta_sanitaria="...")`` directamente porque
el valor en BD está cifrado. Para búsqueda exacta usar un hash separado (futuro).

Uso:
    from core.fields import EncryptedCharField

    class PersonaAtendida(models.Model):
        numero_seguridad_social = EncryptedCharField(max_length=64, blank=True)

Configuración:
    En settings/base.py:
        AGORA_FIELD_ENCRYPTION_KEY = env("AGORA_FIELD_ENCRYPTION_KEY")
    En .env:
        AGORA_FIELD_ENCRYPTION_KEY=<32 bytes en base64 url-safe>

    Generar una clave nueva con:
        python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"

Rotación de clave: documentar en docs/rgpd/rotacion_claves.md (pendiente Fase 3).
"""
from __future__ import annotations

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.db import models


def _get_fernet():
    """Lazy: solo importa Fernet si hay una clave configurada."""
    from cryptography.fernet import Fernet

    key = getattr(settings, "AGORA_FIELD_ENCRYPTION_KEY", None)
    if not key:
        raise ImproperlyConfigured(
            "AGORA_FIELD_ENCRYPTION_KEY no configurada. Genera una con "
            "`python -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())'` "
            "y añádela a backend/.env."
        )
    # Acepta string o bytes
    if isinstance(key, str):
        key = key.encode()
    return Fernet(key)


class EncryptedCharField(models.CharField):
    """CharField cifrado en BD.

    El valor en memoria es siempre el texto plano; el cifrado/descifrado ocurre
    en ``get_prep_value`` (al guardar) y ``from_db_value`` (al leer). Si el valor
    en BD no estaba cifrado (datos previos), se devuelve tal cual — para
    compatibilidad durante la migración inicial.
    """

    description = "CharField cifrado a nivel aplicación (Fernet AES-128)"

    def __init__(self, *args, **kwargs):
        # Forzamos max_length amplio para acomodar el ciphertext (Base64).
        # Si el original es 20 chars, el ciphertext ronda 100-120.
        original_max_length = kwargs.get("max_length", 64)
        kwargs["max_length"] = max(original_max_length * 6, 256)
        self._original_max_length = original_max_length
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        """Permite que makemigrations capture el max_length original."""
        name, path, args, kwargs = super().deconstruct()
        kwargs["max_length"] = self._original_max_length
        return name, path, args, kwargs

    def from_db_value(self, value, expression, connection):
        if value is None or value == "":
            return value
        try:
            f = _get_fernet()
            return f.decrypt(value.encode() if isinstance(value, str) else value).decode()
        except Exception:
            # Valor no cifrado o clave incorrecta: devolverlo crudo
            # (modo compatibilidad con datos previos al cifrado)
            return value

    def to_python(self, value):
        return value

    def get_prep_value(self, value):
        if value is None or value == "":
            return value
        f = _get_fernet()
        cipher = f.encrypt(str(value).encode()).decode()
        return cipher
