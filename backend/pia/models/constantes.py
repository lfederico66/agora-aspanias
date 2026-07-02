"""Constantes del módulo PIA — preguntas, claves, secciones, dimensiones.

Datos de protocolo Aspanias (PV, Historia de Vida, Algo sobre mí, CDV).
"""

PREGUNTAS_HISTORIA_VIDA = [
    ("HV01", "Cómo es tu vida actualmente"),
    ("HV02", "¿Cómo es un día habitual en tu vida actual?"),
    ("HV03", "Qué cosas son importantes para la persona"),
    ("HV04", "Qué es lo que tiene más valor en su vida"),
    ("HV05", "Con qué disfruta. Qué cosas hacen que su vida merezca la pena"),
    ("HV06", "Qué es lo que más echarías de menos si no pudieras hacerlo"),
    ("HV07", "Cómo es un buen día y un mal día"),
    ("HV08", "Cómo era tu vida cuando eras niña/o"),
    ("HV09", "Recuerda actividades en las que disfrutabas cuando eras más joven. ¿Qué tipo de actividades hacía? ¿Qué le gustaba hacer? ¿Qué actividades extraescolares realizaba? ¿Cómo pasaba el tiempo libre? ¿Qué actividades de ocio realizaba? ¿Qué recuerdos guarda de sus amigos de juventud? Cuéntame alguna anécdota."),
    ("HV10", "¿Hacías alguna actividad de ocio con tu familia? Cuéntame algún momento que recuerdes disfrutando con tu familia"),
    ("HV11", "Recuerda algún momento de especial alegría en tu vida. ¿Cuál era la situación? ¿Qué hacías? ¿Quién estaba?"),
    ("HV12", "Qué te gustaba hacer. ¿En qué eres bueno/a?"),
    ("HV13", "¿Qué has estudiado, te gustaría seguir formándote? ¿En qué?"),
    ("HV14", "¿Es importante el trabajo para ti? ¿Has trabajado? ¿En qué? ¿En qué crees que estás más capacitado/a para trabajar?"),
    ("HV15", "¿En qué te gustaría trabajar si encontrases trabajo?"),
    ("HV16", "¿Dónde has estado de vacaciones o de viaje? ¿Y dónde te gustaría ir?"),
    ("HV17", "¿Hay algo que siempre quisiste hacer, pero que no has llegado a realizar nunca?"),
    ("HV18", "Según la gente que te conoce, ¿qué es lo que mejor se le da hacer? ¿Y según ella misma? ¿Qué cosas te gusta hacer ahora?"),
    ("HV19", "¿Hay momentos en los que consigues evadirte de tus problemas haciendo cosas que te gustan? Si es así, ¿cuáles?"),
    ("HV20", "Sé que ahora no es lo mismo que cuando eras joven, pero imagina por un momento que no existe ninguna barrera que te impida realizar aquello que te gustaría. ¿Qué harías? ¿Qué tipo de persona te gustaría ser? ¿Qué estarías haciendo ahora mismo?"),
    ("HV21", "¿Cuáles han sido los momentos más importantes de tu vida? ¿Qué recuerdos querrías volver a vivir, si pudieras?"),
]

CLAVES_RELACION_HISTORIA_VIDA = [
    "Interacción simétrica, es necesaria la humildad por parte de la persona de apoyo.",
    "Escuchar de una manera especial, estando en contacto y centrado en la persona.",
    "Mostrar cercanía de una manera natural.",
    "Expresar empatía, amor, amabilidad y transparencia.",
    "Aprender a no solucionar y validar incondicionalmente la experiencia de la persona.",
    "Actuar con conciencia (notando lo que experimentamos y compartiéndolo) y valentía.",
    "No centrar la conversación en problemas o enfermedades.",
]

SECCIONES_ALGO_SOBRE_MI = [
    ("datos_personales", "Datos personales (situación legal, tutor, prestaciones)"),
    ("salud", "Salud y medicación"),
    ("alimentacion", "Alimentación e ingesta de líquidos"),
    ("sueno_continencia", "Sueño y continencia"),
    ("movilidad", "Movilidad"),
    ("higiene", "Higiene y cuidado personal"),
    ("autonomia_avd", "Autonomía en actividades de la vida diaria"),
    ("comunicacion", "Comunicación"),
    ("salud_mental", "Salud mental y diagnósticos"),
    ("desarrollo_personal", "Desarrollo personal, laboral y de ocio"),
    ("relaciones", "Relaciones interpersonales y espacios que habito"),
]

DIMENSIONES_CDV_SCHALOCK = [
    ("autodeterminacion", "Autodeterminación", "Control personal, elección…", 1),
    ("bienestar_emocional", "Bienestar Emocional", "Felicidad, seguridad…", 2),
    ("bienestar_fisico", "Bienestar Físico", "Salud, nutrición, cuidados básicos…", 3),
    ("bienestar_material", "Bienestar Material", "Tener y disfrutar de pertenencias, tener empleo.", 4),
    ("relaciones", "Relaciones Interpersonales Significativas", "Amigos, familias…", 5),
    ("inclusion_social", "Inclusión Social", "Participar en la comunidad, ser conocido y aceptado.", 6),
    ("desarrollo_personal", "Desarrollo Personal", "Desarrollar habilidades y competencias, tener experiencias nuevas…", 7),
    ("derechos", "Derechos", "Libertades, intimidad, privacidad, dignidad, autonomía, derechos de ciudadanía…", 8),
]

