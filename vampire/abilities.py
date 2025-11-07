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
        ]
    },
    2: {
        "nombre": "Rayo de Escarcha",
        "max_nivel": 5,
        "descripcion_base": "Un proyectil que congela y ralentiza a los enemigos.",
        "niveles": [
            {"damage": 15, "cooldown": 2500, "speed": 8},
            {"damage": 15, "cooldown": 2000, "speed": 8},
            {"damage": 20, "cooldown": 2000, "speed": 10},
            {"damage": 25, "cooldown": 1800, "speed": 10},
            {"damage": 30, "cooldown": 1500, "speed": 12},
        ]
    },
    3: {
        "nombre": "Aura de Fuego",
        "max_nivel": 5,
        "descripcion_base": "Aura que quema a los enemigos cercanos periódicamente.",
        "niveles": [
            {"damage": 3, "cooldown": 1000, "radius": 1.0}, # Multiplicador de radio base
            {"damage": 5, "cooldown": 1000, "radius": 1.2},
            {"damage": 7, "cooldown": 900, "radius": 1.2},
            {"damage": 9, "cooldown": 800, "radius": 1.5},
            {"damage": 12, "cooldown": 700, "radius": 1.7},
        ]
    },
    4: {
        "nombre": "Bumerang Gigante",
        "max_nivel": 6,
        "descripcion_base": "Lanza un proyectil que regresa al jugador.",
        "niveles": [
            {"damage": 20, "cooldown": 3000, "speed": 7, "lifetime": 150, "count": 1},
            {"damage": 25, "cooldown": 2800, "speed": 7, "lifetime": 150, "count": 1},
            {"damage": 30, "cooldown": 2800, "speed": 8, "lifetime": 180, "count": 1},
            {"damage": 35, "cooldown": 2500, "speed": 8, "lifetime": 180, "count": 1},
            {"damage": 40, "cooldown": 2500, "speed": 9, "lifetime": 200, "count": 2},
            {"damage": 50, "cooldown": 2000, "speed": 10, "lifetime": 220, "count": 2},
        ]
    },
    5: {
        "nombre": "Aura de Magnetismo",
        "max_nivel": 3,
        "descripcion_base": "Aumenta el radio de recolección de experiencia.",
        "niveles": [
            {"damage": 0, "cooldown": 500, "radius": 1.5}, # Multiplicador de radio de recolección
            {"damage": 0, "cooldown": 500, "radius": 2.0},
            {"damage": 0, "cooldown": 500, "radius": 3.0},
        ]
    }
}

# -------------------------------------------------
# LÓGICA DE NIVELADO
# -------------------------------------------------

def obtener_opciones_subida_nivel(active_abilities: Dict[int, int], num_opciones: int = 3) -> List[Option]:
    """
    Genera una lista de opciones únicas para que el jugador elija al subir de nivel.
    Prioriza las mejoras de habilidades activas.
    """
    opciones: List[Option] = []
    usadas = set() # Para asegurar opciones únicas
    rng = random.Random()
    
    # Probabilidad base de que se ofrezca una mejora (en lugar de una nueva habilidad)
    prob_mejora = 0.7 

    # Habilidades que ya tiene el jugador
    habilidades_activas = active_abilities.keys()
    # Habilidades que aún no están al máximo
    mejores_disponibles = [
        hid for hid in habilidades_activas
        if active_abilities[hid] < HABILIDADES_MAESTRAS[hid]["max_nivel"]
    ]
    # Habilidades que el jugador no tiene
    nuevas = [
        hid for hid in HABILIDADES_MAESTRAS.keys() 
        if hid not in habilidades_activas
    ]
    
    for _ in range(num_opciones):
        # Candidatos que no se han usado
        cand_mej = [hid for hid in mejores_disponibles if (hid, "Mejora") not in usadas]
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
def describir_opcion(opcion: Option, active_abilities: Dict[int, int]) -> str:
    """Devuelve texto legible para mostrar al jugador. (Acepta active_abilities para saber el nivel)"""
    hid, tipo = opcion
    hab = HABILIDADES_MAESTRAS[hid]
    nivel_actual = active_abilities.get(hid, 0)
    
    if tipo == "Nueva":
         return f"NUEVO: {hab['nombre']}. {hab['descripcion_base']}"
    
    elif tipo == "Mejora":
        nivel_siguiente = nivel_actual + 1
        
        if nivel_siguiente > hab["max_nivel"]:
             return f"MAX: {hab['nombre']} (Nv. {nivel_actual})."
             
        # Obtener los parámetros del nivel actual y siguiente
        params_actual = hab["niveles"][nivel_actual - 1] 
        params_siguiente = hab["niveles"][nivel_siguiente - 1] 
        
        desc = f"MEJORA: {hab['nombre']} (Nv. {nivel_actual} -> {nivel_siguiente}). "
        cambios = []
        
        # Comparar las métricas comunes
        for key in params_actual.keys():
            if params_actual[key] != params_siguiente[key]:
                if key == "damage":
                    cambios.append(f"Daño: {params_actual[key]} -> {params_siguiente[key]}")
                elif key == "cooldown":
                    cambios.append(f"CD: {params_actual[key]//1000}s -> {params_siguiente[key]//1000}s")
                elif key == "count":
                    cambios.append(f"Cant.: {params_actual[key]} -> {params_siguiente[key]}")
                elif key == "radius":
                    cambios.append(f"Radio x{params_actual[key]:.1f} -> x{params_siguiente[key]:.1f}")
                    
        return desc + ", ".join(cambios)
        
    return "Opción desconocida."