# abilities.py (SOLO SE MUESTRA EL CAMBIO EN ID 2)
# ... (código existente) ...

# HABILIDADES MAESTRAS
HABILIDADES_MAESTRAS: Dict[int, Dict[str, Any]] = {
    1: { 
        # ... Daga Rápida (ya tiene sprite) ...
    },
    2: {
        "nombre": "Rayo de Escarcha",
        "max_nivel": 5,
        # Descripción actualizada
        "descripcion_base": "Dispara un gran copo de nieve (❄️) que congela enemigos.",
        "niveles": [
            {"damage": 10, "freeze_duration": 500, "cooldown": 3000},
            # ... (otros niveles) ...
        ],
    },
    3: {
        "nombre": "Aura de Fuego",
        "max_nivel": 7,
        # Descripción actualizada
        "descripcion_base": "Un aura de llamas (🔥) que daña y gira constantemente.",
        "niveles": [
            # ... (niveles) ...
        ],
    },
    4: { 
        # ... Bumerán Gigante (ya tiene sprite) ...
    },
    # ... (código restante) ...
}