# Decisión 06 — Valoraciones psicológicas

**Fecha**: 2026-06-16
**Decisor**: Federico Martínez · Gerencia
**Ámbito**: área de Psicología del Grupo Social Aspanias
**Estado**: Aprobado · implementación en curso

---

## 1. Origen

El equipo de Psicología (centro Fuentecillas y resto del grupo) aplica
regularmente un conjunto de escalas, pruebas e informes que hoy se rellenan
en Word/Excel sueltos, sin trazabilidad ni vínculo con el resto de la ficha
de la persona atendida. Federico aporta la categorización en
`1. listados escalas para nueva plataforma.docx` y solicita que ÁGORA
permita **cumplimentar online + imprimir** estas valoraciones.

## 2. Categorización aprobada

Estructura jerárquica del docx aportado:

```
ESCALAS E INFORMES DE VALORACIÓN PSICOLÓGICA

├── Escalas adaptativas
│   ├── ICAP
│   └── ABS-RC:2
│
├── Escalas de calidad de vida
│   ├── SAN MARTÍN
│   ├── FUMAT
│   └── INICO-FEAPS
│
├── Pruebas de valoración y evaluación
│   ├── Conductas
│   │   └── BBTA
│   ├── Inteligencia
│   │   ├── K-BIT
│   │   ├── Raven
│   │   └── WISC-4
│   ├── Personalidad
│   │   └── DSAH II
│   └── Deterioro cognitivo
│       ├── Camdex DS
│       ├── MEC
│       └── Test Barcelona
│
├── Escalas diagnóstico / screening trastornos mentales
│   └── DSAH II
│
└── Informes psicológicos
    ├── Inicial
    └── Evolutivo
```

**Total**: 6 categorías · 13 escalas únicas · 2 tipos de informe.

## 3. Decisiones técnicas

### Modelo de datos
- **Reutilizar** `intervenciones.Valoracion` (ya existente) ampliándolo —
  no crear app nueva. La valoración es una forma específica de intervención.
- Añadir `categoria` (6 valores), ampliar `instrumento` (de 7 a 19 opciones),
  añadir `respuestas` y `puntuacion` JSON polimórficos, `estado`, `firmada_por`,
  `pdf_generado`.
- **Nuevo modelo** `InformePsicologico` (inicial / evolutivo) con `contenido`
  JSON polimórfico, profesional firmante y `numero_colegiado`.

### Estructura JSON `respuestas`
Cada escala tiene su esquema. Almacenamos respuestas literalmente como las
introduce el psicólogo, sin pre-procesar. Las puntuaciones se calculan
on-the-fly o se guardan en `puntuacion` cuando el cálculo es costoso.

Ejemplo para ICAP:
```json
{
  "version": "icap_v1",
  "destrezas_motoras": { "items": {...}, "subtotal": 38 },
  "destrezas_sociales": {...},
  "destrezas_vida_personal": {...},
  "destrezas_vida_comunidad": {...},
  "problemas_conducta": {...}
}
```

### Estructura JSON `contenido` (informes)
**Inicial** — secciones extraídas de la plantilla real:
- antecedentes_personales (embarazo, enfermedades, órganos sentidos, etc.)
- antecedentes_familiares
- nivel_autonomia (AVD básicas, instrumentales, avanzadas)
- esfera_conducta (ambiente familiar/social, hábitos tóxicos, fugas, robos)
- caracterologia (alegre/triste, sociable/solitario, etc.)
- aficiones, estudios, trabajos
- tratamiento_actual
- exploracion_psicopatologica (apariencia, comunicación, conciencia,
  orientación, atención, memoria, ánimo, fobias, pensamiento abstracto,
  funciones ejecutivas, praxias, gnosias, sensopercepción, juicio,
  control impulsos)
- ubicacion_actual_plaza_asignada

**Evolutivo** — secciones extraídas de la plantilla real:
- funciones_cognitivas (comunicación, conciencia, orientación, atención,
  memoria, razonamiento, juicio, control impulsos)
- funciones_instrumentales (praxias + gnosias)
- aspectos_conductuales_emocionales (cambios significativos respecto a la
  valoración anterior)
- integracion_centro
- grado_minusvalia, valoracion_dependencia, icap

## 4. Cobertura del material (jun 2026)

| Instrumento | Material aportado por Federico | Implementación demo |
|---|---|---|
| ICAP | Cuadernillo PDF + Manual PDF | ✓ Formulario muestra |
| ABS-RC:2 | Excel con 14 dominios | ✓ Esqueleto + plantilla |
| San Martín | PDF (8 MB) | ✓ Esqueleto |
| FUMAT | PDF (2,5 MB) | ✓ Esqueleto |
| INICO-FEAPS | PDF (0,9 MB) | ✓ Esqueleto |
| Informe Inicial | docx | ✓ Formulario completo (~50 secciones) |
| Informe Evolutivo | docx | ✓ Formulario completo |
| BBTA, K-BIT, Raven, WISC-4, DSAH II, Camdex DS, MEC, Test Barcelona | Sin material | "Próximamente" en UI |

## 5. Decisiones UX

### Categorización en UI
Replicar literalmente la estructura del docx en `valoraciones-listado.html`
(5 categorías visibles + sub-categorías de "Pruebas de valoración" como
sub-bloques plegables).

### Cumplimentación
- Formularios HTMX con auto-guardado por sección
- Estado `borrador` → `completada` → `firmada` (irreversible)
- Trazabilidad: aplicado_por + firmada_por + bitácora RGPD

### PDF imprimible
**Formato A4 institucional ÁGORA** — no reproduce el cuadernillo editorial
original (evita problemas de copyright):
- Cabecera con logo Fundación Aspanias Burgos
- Datos persona (nombre completo, fecha nacimiento, centro)
- Datos valoración (instrumento, fecha aplicación, profesional)
- Ítems completados + puntuaciones
- Conclusiones
- Casilla firma profesional + nº colegiado

## 6. RGPD

Las valoraciones psicológicas son **categoría especial art. 9 RGPD**
(datos de salud). Aplica:
- Acceso restringido a rol `clinico` (psicólogo, dirección de centro)
- Bitácora obligatoria de cada lectura
- Cifrado en reposo
- Retención mínima conforme a Ley 41/2002 (5 años post-baja)

## 7. Próximos pasos previstos

- Iterar formularios de las 4 escalas con PDF aportado (FUMAT, INICO, San Martín, ABS-RC:2) — requiere Federico/Psicología aporte detalle de ítems
- Sistema de baremos automáticos (conversión puntuación → percentil) cuando se aporten tablas
- Conectar Valoracion ↔ PIA (objetivos del PV pueden disparar valoración periódica)
- Sistema de alertas: revaloración periódica obligatoria por instrumento
