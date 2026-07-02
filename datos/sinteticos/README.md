# Datos sintéticos ÁGORA

Cero datos reales. Todo lo que viva en esta carpeta o se genere por el comando `cargar_datos_sinteticos` es ficticio (Faker en español).

## Generación

```bash
make datos-sinteticos
# o, con argumento:
docker compose -f infraestructura/docker-compose.yml exec web python manage.py cargar_datos_sinteticos --personas 50
```

## Distribución por colectivo (pesos por defecto)

| Colectivo | Peso | Centros tipo |
|---|---|---|
| Discapacidad intelectual | 40 % | Fuentecillas, Lara |
| Mayores dependientes | 35 % | Salas, Villadiego |
| Inserción laboral | 15 % | CEE Burgos |
| Familias (DI) | 10 % | Fuentecillas, Lara |

## Recordatorio RGPD

Esta carpeta nunca debe contener exportaciones de producción ni copias parciales de Odoo. Si necesitas probar contra datos reales, hazlo solo en entorno aislado y nunca lo subas al repo.
