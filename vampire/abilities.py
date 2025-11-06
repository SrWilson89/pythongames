# abilities.py
import random
from typing import Dict, List, Tuple, Literal, Any

# -------------------------------------------------
# TIPOS PARA MEJOR LEGIBILIDAD
# -------------------------------------------------
OptionType = Literal["Mejora", "Nueva"]
Option = Tuple[int, OptionType]  # (id_habilidad, tipo)

# -------------------------------------------------
# HABILIDADES MAESTRAS
# -------------------------------------------------
HABILIDADES_MAESTRAS: Dict[int, Dict[str, Any]] = {
    1: {
        "nombre": "Daga Rápida",
        "max_nivel": 8,
        "descripcion_base": "Dispara dagas en direcciones aleatorias.",
        "niveles": [
            {"damage": 5,  "cooldown": 1000, "count": 1},
            {"damage": 5,  "cooldown":  900, "count": 1},
            {"damage": 7,  "cooldown":  900, "count": 1},
            {"damage": 7,  "cooldown":  800, "count": 1},
            {"damage": 8,  "cooldown":  800, "count": 2},
            {"damage": 9,  "cooldown":  700, "count": 2},
            {"damage": 10, "cooldown":  700, "count": 3},
            {"damage": 12, "cooldown":  600, "count": 3},
        ],
    },
    2: {
        "nombre": "Rayo de Escarcha",
        "max_nivel": 5,
        "descripcion_base": "El rayo congela más tiempo.",
        "niveles": [ # Relleno de niveles para evitar errores
            {"damage": 10, "freeze_duration": 500, "cooldown": 3000},
            {"damage": 12, "freeze_duration": 600, "cooldown": 2800},
            {"damage": 14, "freeze_duration": 700, "cooldown": 2600},
            {"damage": 16, "freeze_duration": 800, "cooldown": 2400},
            {"damage": 20, "freeze_duration": 900, "cooldown": 2200},
        ],
    },
    3: {
        "nombre": "Aura de Fuego",
        "max_nivel": 7,
        "descripcion_base": "Un aura persistente que daña a enemigos cercanos.",
        "niveles": [
            {"damage": 2, "radius": 50,  "cooldown": 800},
            {"damage": 3, "radius": 50,  "cooldown": 700},
            {"damage": 3, "radius": 70,  "cooldown": 700},
            {"damage": 4, "radius": 70,  "cooldown": 600},
            {"damage": 5, "radius": 90,  "cooldown": 600},
            {"damage": 6, "radius": 90,  "cooldown": 500},
            {"damage": 7, "radius": 100, "cooldown": 500},
        ],
    },
    4: {
        "nombre": "Bumerán Gigante",
        "max_nivel": 6,
        "descripcion_base": "Lanza bumeranes que regresan.",
        "niveles": [
            {"damage": 8,  "speed": 6, "lifetime": 150, "cooldown": 2500, "count": 1},
            {"damage": 8,  "speed": 7, "lifetime": 150, "cooldown": 2200, "count": 1},
            {"damage": 10, "speed": 7, "lifetime": 180, "cooldown": 2200, "count": 1},
            {"damage": 10, "speed": 8, "lifetime": 180, "cooldown": 2000, "count": 2},
            {"damage": 12, "speed": 9, "lifetime": 200, "cooldown": 2000, "count": 2},
            {"damage": 15, "speed": 9, "lifetime": 200, "cooldown": 1800, "count": 3},
        ],
    },
    5: {
        "nombre": "Escudo Defensivo",
        "max_nivel": 4,
        "descripcion_base": "Aumenta la duración del escudo.",
        "niveles": [ # Relleno de niveles para evitar errores
            {"defense_boost": 5, "duration": 3000, "cooldown": 15000},
            {"defense_boost": 8, "duration": 3500, "cooldown": 14000},
            {"defense_boost": 10, "duration": 4000, "cooldown": 13000},
            {"defense_boost": 12, "duration": 5000, "cooldown": 12000},
        ],
    },
}

# -------------------------------------------------
# UTILIDADES
# -------------------------------------------------
def _ids_mejorables(habilidades_activas: Dict[int, int]) -> List[int]:
    """Devuelve lista de IDs que pueden subir de nivel."""
    return [
        hid for hid, nivel in habilidades_activas.items()
        if nivel < HABILIDADES_MAESTRAS[hid]["max_nivel"]
    ]

def _ids_nuevas(habilidades_activas: Dict[int, int]) -> List[int]:
    """Devuelve lista de IDs que aún no están desbloqueadas."""
    return list(set(HABILIDADES_MAESTRAS.keys()) - habilidades_activas.keys())

# -------------------------------------------------
# SELECCIÓN DE OPCIONES
# -------------------------------------------------
def obtener_opciones_subida_nivel(
    habilidades_activas: Dict[int, int],
    *,
    num_opciones: int = 3,
    prob_mejora: float = 0.7,
    rng: random.Random = random
) -> List[Option]:
    """
    Genera `num_opciones` opciones únicas para subir de nivel.
    """
    opciones: List[Option] = []
    usadas = set()  # (id, tipo)

    mejorables = _ids_mejorables(habilidades_activas)
    nuevas = _ids_nuevas(habilidades_activas)

    while len(opciones) < num_opciones and (mejorables or nuevas):
        # Candidatos que aún no hemos usado
        cand_mej = [hid for hid in mejorables if (hid, "Mejora") not in usadas]
        cand_nue = [hid for hid in nuevas     if (hid, "Nueva")  not in usadas]

        # ¿Elegimos mejora o nueva?
        elige_mejora = (
            cand_mej and
            (rng.random() < prob_mejora or not cand_nue)
        )

        if elige_mejora and cand_mej:
            elegido = rng.choice(cand_mej)
            tipo: OptionType = "Mejora"
        elif cand_nue:
            elegido = rng.choice(cand_nue)
            tipo = "Nueva"
        else:
            # Último recurso: lo que quede
            if cand_mej:
                elegido = rng.choice(cand_mej)
                tipo = "Mejora"
            else:
                break  # nada más que ofrecer

        opciones.append((elegido, tipo))
        usadas.add((elegido, tipo))

    return opciones

# -------------------------------------------------
# HELPERS PARA UI / DEBUG
# -------------------------------------------------
def describir_opcion(opcion: Option) -> str:
    """Devuelve texto legible para mostrar al jugador."""
    hid, tipo = opcion
    hab = HABILIDADES_MAESTRAS[hid]
    nivel = 1 if tipo == "Nueva" else None  # se calcula después
    prefijo = "NUEVA →" if tipo == "Nueva" else "MEJORA →"
    return f"{prefijo} {hab['nombre']}"