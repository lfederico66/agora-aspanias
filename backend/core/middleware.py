"""Middleware de bitácora — registra accesos relevantes a ÁGORA."""
import re

from .models import RegistroAcceso

RUTAS_AUDITADAS = re.compile(r"^/(personas|planes-vida|intervenciones|agenda|indicadores)/")
RUTAS_IGNORADAS = re.compile(r"^/(static|media|admin/jsi18n|favicon)")


class BitacoraAccesoMiddleware:
    """Registra cada acceso autenticado a rutas sensibles.

    No registra navegación a /static, /media o login. La idea es no inflar la
    bitácora con ruido y mantenerla útil para auditoría RGPD.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        try:
            self._registrar(request, response)
        except Exception:
            # Nunca romper la respuesta por fallo de bitácora.
            # En prod, se reportará a logging.
            pass
        return response

    def _registrar(self, request, response):
        if not request.user.is_authenticated:
            return
        path = request.path or ""
        if RUTAS_IGNORADAS.match(path):
            return
        if not RUTAS_AUDITADAS.match(path):
            return

        accion = self._inferir_accion(request.method)
        persona_id = self._extraer_persona_id(path)

        RegistroAcceso.objects.create(
            profesional=request.user if request.user.is_authenticated else None,
            persona_consultada_id=persona_id,
            accion=accion,
            entidad=path.strip("/").split("/")[0] if path else "",
            ruta=path[:512],
            ip=self._ip_cliente(request),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:512],
        )

    @staticmethod
    def _inferir_accion(metodo: str) -> str:
        return {
            "GET": RegistroAcceso.Accion.LEER,
            "POST": RegistroAcceso.Accion.EDITAR,
            "PUT": RegistroAcceso.Accion.EDITAR,
            "PATCH": RegistroAcceso.Accion.EDITAR,
            "DELETE": RegistroAcceso.Accion.ELIMINAR,
        }.get(metodo, RegistroAcceso.Accion.LEER)

    @staticmethod
    def _extraer_persona_id(path: str):
        m = re.search(
            r"/personas/([0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})",
            path,
        )
        return m.group(1) if m else None

    @staticmethod
    def _ip_cliente(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")
