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
        "max_nivel": 10,
        "descripcion_base": "Dispara dagas en direcciones aleatorias.",
        "niveles": [
            {"damage": 5,  "cooldown": 1000, "count": 1},
            {"damage": 5,  "cooldown":  900, "count": 2},
            {"damage": 7,  "cooldown":  900, "count": 3},
            {"damage": 7,  "cooldown":  800, "count": 4},
            {"damage": 8,  "cooldown":  800, "count": 5},
            {"damage": 9,  "cooldown":  700, "count": 6},
            {"damage": 10, "cooldown":  700, "count": 7},
            {"damage": 12, "cooldown":  600, "count": 8},
            {"damage": 14, "cooldown":  550, "count": 9},
            {"damage": 16, "cooldown":  500, "count": 10},
        ]
    },
    2: {
        "nombre": "Rayo de Escarcha",
        "max_nivel": 10,
        "descripcion_base": "Dispara un rayo que atraviesa a los enemigos.",
        "niveles": [
            {"damage": 10, "cooldown": 2500, "speed": 8},
            {"damage": 15, "cooldown": 2200, "speed": 8},
            {"damage": 20, "cooldown": 2000, "speed": 10},
            {"damage": 30, "cooldown": 2000, "speed": 10},
            {"damage": 50, "cooldown": 1800, "speed": 12},
            {"damage": 65, "cooldown": 1700, "speed": 12},
            {"damage": 80, "cooldown": 1600, "speed": 14},
            {"damage": 100, "cooldown": 1500, "speed": 14},
            {"damage": 125, "cooldown": 1400, "speed": 16},
            {"damage": 150, "cooldown": 1300, "speed": 18},
        ]
    },
    3: {
        "nombre": "Aura de Fuego",
        "max_nivel": 10,
        "descripcion_base": "Un anillo de fuego que quema a los enemigos cercanos.",
        "niveles": [
            {"damage": 3,   "cooldown": 1000, "radius": 1.0},
            {"damage": 5,   "cooldown": 500,  "radius": 1.2},
            {"damage": 8,   "cooldown": 300,  "radius": 1.5},
            {"damage": 15,  "cooldown": 150,  "radius": 1.8},
            {"damage": 30,  "cooldown": 70,   "radius": 2.0},
            {"damage": 45,  "cooldown": 60,   "radius": 2.2},
            {"damage": 60,  "cooldown": 50,   "radius": 2.4},
            {"damage": 80,  "cooldown": 40,   "radius": 2.6},
            {"damage": 100, "cooldown": 30,   "radius": 2.8},
            {"damage": 130, "cooldown": 25,   "radius": 3.0},
        ]
    },
    4: {
        "nombre": "Bumerán Gigante",
        "max_nivel": 10,
        "descripcion_base": "Lanza un bumerán que regresa y golpea dos veces.",
        "niveles": [
            {"damage": 15, "cooldown": 4000, "speed": 5, "lifetime": 150, "count": 1},
            {"damage": 20, "cooldown": 3800, "speed": 6, "lifetime": 160, "count": 2},
            {"damage": 20, "cooldown": 3500, "speed": 6, "lifetime": 170, "count": 3},
            {"damage": 25, "cooldown": 3500, "speed": 7, "lifetime": 180, "count": 4},
            {"damage": 30, "cooldown": 3000, "speed": 8, "lifetime": 200, "count": 5},
            {"damage": 35, "cooldown": 2800, "speed": 8, "lifetime": 210, "count": 6},
            {"damage": 40, "cooldown": 2600, "speed": 9, "lifetime": 220, "count": 7},
            {"damage": 45, "cooldown": 2400, "speed": 9, "lifetime": 230, "count": 8},
            {"damage": 50, "cooldown": 2200, "speed": 10, "lifetime": 240, "count": 9},
            {"damage": 60, "cooldown": 2000, "speed": 10, "lifetime": 250, "count": 10},
        ]
    },
    5: {
        "nombre": "Bomba Aleatoria",
        "max_nivel": 10,
        "descripcion_base": "Lanza bombas que explotan en un área, golpeando a los enemigos.",
        "niveles": [
            {"damage": 20,  "cooldown": 5000, "radius": 1.0, "count": 1,  "fall_time": 60},
            {"damage": 25,  "cooldown": 4500, "radius": 1.2, "count": 2,  "fall_time": 60},
            {"damage": 25,  "cooldown": 4000, "radius": 1.5, "count": 3,  "fall_time": 50},
            {"damage": 30,  "cooldown": 4000, "radius": 1.8, "count": 4,  "fall_time": 50},
            {"damage": 40,  "cooldown": 3500, "radius": 2.0, "count": 5,  "fall_time": 40},
            {"damage": 50,  "cooldown": 3200, "radius": 2.2, "count": 6,  "fall_time": 40},
            {"damage": 60,  "cooldown": 2900, "radius": 2.4, "count": 7,  "fall_time": 35},
            {"damage": 75,  "cooldown": 2600, "radius": 2.6, "count": 8,  "fall_time": 35},
            {"damage": 90,  "cooldown": 2300, "radius": 2.8, "count": 9,  "fall_time": 30},
            {"damage": 110, "cooldown": 2000, "radius": 3.0, "count": 10, "fall_time": 30},
        ]
    },
}

# -------------------------------------------------
# Funciones de Soporte
# -------------------------------------------------
def obtener_opciones_subida_nivel(active_abilities: Dict[int, int]) -> List[Option]:
    available_new_ids = [hid for hid in HABILIDADES_MAESTRAS.keys() if hid not in active_abilities]
    available_upgrade_ids = [
        hid for hid, level in active_abilities.items()
        if level < HABILIDADES_MAESTRAS[hid]["max_nivel"]
    ]
    all_options: List[Option] = (
        [(hid, "Nueva") for hid in available_new_ids] +
        [(hid, "Mejora") for hid in available_upgrade_ids]
    )
    if not all_options:
        return []
    num_choices = min(3, len(all_options))
    return random.sample(all_options, num_choices)


def describir_opcion(hid: int, tipo: str, active_abilities: Dict[int, int]) -> str:
    hab = HABILIDADES_MAESTRAS[hid]
    nivel_actual = active_abilities.get(hid, 0)

    if tipo == "Nueva":
        return f"NUEVO: {hab['nombre']}. {hab['descripcion_base']}"

    elif tipo == "Mejora":
        nivel_siguiente = nivel_actual + 1
        if nivel_siguiente > hab["max_nivel"]:
            return f"MAX: {hab['nombre']} (Nv. {nivel_actual})."

        params_actual = hab["niveles"][nivel_actual - 1]
        params_siguiente = hab["niveles"][nivel_siguiente - 1]

        desc = f"MEJORA: {hab['nombre']} (Nv. {nivel_actual} -> {nivel_siguiente}). "
        cambios = []

        for key in params_actual.keys():
            if key not in params_siguiente:
                continue
            if params_actual[key] != params_siguiente[key]:
                if key == "damage":
                    cambios.append(f"Daño: {params_actual[key]} -> {params_siguiente[key]}")
                elif key == "cooldown":
                    cambios.append(f"CD: {params_actual[key]//1000}s -> {params_siguiente[key]//1000}s")
                elif key == "count":
                    cambios.append(f"Cant.: {params_actual[key]} -> {params_siguiente[key]}")
                elif key == "radius":
                    cambios.append(f"Radio: x{params_actual[key]} -> x{params_siguiente[key]}")
                elif key == "fall_time":
                    cambios.append(f"Tiempo Caída: {params_actual[key]}f -> {params_siguiente[key]}f")
                elif key == "lifetime":
                    cambios.append(f"Duración: {params_actual[key]}f -> {params_siguiente[key]}f")
                elif key == "speed":
                    cambios.append(f"Velocidad: {params_actual[key]} -> {params_siguiente[key]}")

        return desc + ", ".join(cambios) + "."