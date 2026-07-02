"""Reemplazos puntuales de nombres de centros antiguos que se escaparon."""
from pathlib import Path

DEMO = Path(__file__).resolve().parent.parent / "demo"

PARCHES = [
    ("agenda-hoy.html",     "solapamiento de 30 min con coordinación Las Calzadas", "solapamiento de 30 min con coordinación V. Aleixandre"),
    ("control-pv.html",     "Centro de Día Las Calzadas",                            "CD Aspanias Puentesaúco"),
    ("gestores-caso.html",  "Vivienda San Pedro",                                    "Áreas de Vivienda"),
    ("gestores-caso.html",  "Centro Promoción Salas",                                "CD Aspanias Salas"),
    ("indicadores.html",    "Centro de Día Las Calzadas",                            "CD Aspanias Puentesaúco"),
    ("personas-lista.html", "CEE CISA Burgos",                                       "Colegio EE Puentesaúco"),
]

for nombre, viejo, nuevo in PARCHES:
    ruta = DEMO / nombre
    contenido = ruta.read_text(encoding="utf-8")
    if viejo in contenido:
        nuevo_contenido = contenido.replace(viejo, nuevo)
        ruta.write_text(nuevo_contenido, encoding="utf-8")
        print(f"[OK] {nombre}: '{viejo[:40]}...' -> '{nuevo[:40]}...'")
    else:
        print(f"[ ] {nombre}: '{viejo[:40]}...' no encontrado")
