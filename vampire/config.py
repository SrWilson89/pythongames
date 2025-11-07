# config.py
import pygame
import sys

# Inicializamos Pygame temporalmente para obtener la información de la pantalla
pygame.init() 
try:
    info = pygame.display.Info()
    # Usamos la resolución actual del monitor
    SCREEN_WIDTH = info.current_w
    SCREEN_HEIGHT = info.current_h
except pygame.error:
    # Fallback si no se puede inicializar (para entornos sin display)
    SCREEN_WIDTH = 800
    SCREEN_HEIGHT = 600
    print("Advertencia: No se pudo obtener la resolución de pantalla, usando 800x600.")
    
# Detenemos pygame para evitar doble inicialización
pygame.quit() 
# Reiniciamos la inicialización en main.py para asegurar el orden correcto.

# --- Configuración de la Ventana ---
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)
FPS = 60
TITLE = "Vampire Survivors Pixel Clone - ESCALA MÁXIMA"

# --- Colores (en RGB) ---
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 200, 0)
RED = (200, 0, 0)
BLUE = (0, 0, 200)

# --- Configuración del Juego ---
TILE_SIZE = 64  # ¡Tamaño base para sprites (Aumentado de 32 a 64)!
PLAYER_START_SPEED = 3
EXPERIENCE_PER_LEVEL = 2