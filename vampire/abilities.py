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
        "descripcion_base": "Dispara un rayo que atraviesa a los enemigos.",
        "niveles": [
            {"damage": 10, "cooldown": 2500, "speed": 8},
            {"damage": 15, "cooldown": 2200, "speed": 8},
            {"damage": 15, "cooldown": 2000, "speed": 10},
            {"damage": 20, "cooldown": 2000, "speed": 10},
            {"damage": 25, "cooldown": 1800, "speed": 12},
        ]
    },
    3: {
        "nombre": "Aura de Fuego",
        "max_nivel": 5,
        "descripcion_base": "Un anillo de fuego que quema a los enemigos cercanos.",
        "niveles": [
            {"damage": 3,  "cooldown": 1000, "radius": 1.0}, # Daño cada 1s
            {"damage": 5,  "cooldown": 1000, "radius": 1.2},
            {"damage": 5,  "cooldown": 800, "radius": 1.2},
            {"damage": 7,  "cooldown": 800, "radius": 1.5},
            {"damage": 10, "cooldown": 600, "radius": 1.5},
        ]
    },
    4: {
        "nombre": "Bumerán Gigante",
        "max_nivel": 5,
        "descripcion_base": "Lanza un bumerán que regresa y golpea dos veces.",
        "niveles": [
            {"damage": 15, "cooldown": 4000, "speed": 5, "lifetime": 150, "count": 1},
            {"damage": 20, "cooldown": 3800, "speed": 6, "lifetime": 160, "count": 1},
            {"damage": 20, "cooldown": 3500, "speed": 6, "lifetime": 170, "count": 1},
            {"damage": 25, "cooldown": 3500, "speed": 7, "lifetime": 180, "count": 2},
            {"damage": 30, "cooldown": 3000, "speed": 8, "lifetime": 200, "count": 2},
        ]
    },
    5: { # NUEVA HABILIDAD
        "nombre": "Bomba Aleatoria",
        "max_nivel": 5,
        "descripcion_base": "Lanza bombas que explotan en un área, golpeando a los enemigos.",
        "niveles": [
            {"damage": 20, "cooldown": 5000, "radius": 1.0, "count": 1, "fall_time": 60}, # Cooldown de 5s
            {"damage": 25, "cooldown": 4500, "radius": 1.0, "count": 1, "fall_time": 60},
            {"damage": 25, "cooldown": 4000, "radius": 1.2, "count": 1, "fall_time": 50},
            {"damage": 30, "cooldown": 4000, "radius": 1.2, "count": 2, "fall_time": 50},
            {"damage": 40, "cooldown": 3500, "radius": 1.5, "count": 2, "fall_time": 40},
        ]
    },
}

# ... (El resto de las funciones auxiliares se mantienen igual) ...

# Funciones de Soporte
# -------------------------------------------------

def obtener_opciones_subida_nivel(active_abilities: Dict[int, int]) -> List[Option]:
    # ... (código sin cambios)
    
    # Lista de IDs de habilidades disponibles para "Nueva"
    available_new_ids = [hid for hid in HABILIDADES_MAESTRAS.keys() if hid not in active_abilities]
    
    # Lista de IDs de habilidades disponibles para "Mejora"
    available_upgrade_ids = [
        hid for hid, level in active_abilities.items() 
        if level < HABILIDADES_MAESTRAS[hid]["max_nivel"]
    ]
    
    # Combinar todas las opciones
    all_options: List[Option] = (
        [(hid, "Nueva") for hid in available_new_ids] + 
        [(hid, "Mejora") for hid in available_upgrade_ids]
    )
    
    # Si no hay opciones, devolver lista vacía
    if not all_options:
        return []

    # Elegir 3 opciones aleatorias sin repetición
    num_choices = min(3, len(all_options))
    return random.sample(all_options, num_choices)


def describir_opcion(hid: int, tipo: str, active_abilities: Dict[int, int]) -> str:
    # ... (código sin cambios)
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
            if key not in params_siguiente: continue # Ignorar claves que desaparecen (no debería pasar)
            
            if params_actual[key] != params_siguiente[key]:
                if key == "damage":
                    cambios.append(f"Daño: {params_actual[key]} -> {params_siguiente[key]}")
                elif key == "cooldown":
                    # Muestra el cooldown en segundos
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