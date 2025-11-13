# enemies.py - VERSIÓN CORREGIDA
import pygame
import math
import random 
import os # Importación necesaria para resource_path
import sys # Importación necesaria para resource_path
from config import TILE_SIZE, RED, WHITE, GREEN

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA (Añadida para PyInstaller)
# =======================================================
def resource_path(relative_path):
    """
    Función que maneja rutas de recursos para desarrollo local o
    ejecutables empaquetados por PyInstaller.
    """
    try:
        # sys._MEIPASS es la ruta de la carpeta temporal que PyInstaller crea
        base_path = sys._MEIPASS
    except Exception:
        # Si no está empaquetado (se ejecuta localmente), usa la ruta actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# =======================================================

# Lista de sprites de enemigos disponibles (incluyendo enemy.png, enemy1.png, enemy2.png)
ENEMY_SPRITES = ["enemy.png", "enemy1.png", "enemy2.png", "enemy3.png", "enemy4.png", "enemy5.png", "enemy6.png", "enemy7.png", "enemy8.png", "enemy9.png", "enemy10.png", "enemy11.png", "enemy12.png"] 

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target, groups, health_multiplier=1.0):
        super().__init__(groups)
        
        self.target = target
        
        # --- Lógica de Salud con Multiplicador y Velocidad ---
        base_health = 10
        self.health = base_health * health_multiplier 
        self.max_health = base_health * health_multiplier
        self.speed = 1.5 
        
        # --- LÓGICA DE SPRITE ALEATORIO ---
        chosen_sprite = random.choice(ENEMY_SPRITES)
        sprite_path = f"assets/sprites/{chosen_sprite}"
        
        # Carga y escala el sprite del enemigo
        try:
            # Usa resource_path para la carga
            original_image = pygame.image.load(resource_path(sprite_path)).convert_alpha() 
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
            
            # Animación simple de flip basado en la dirección
            if x > target.rect.centerx: # Si el enemigo está a la derecha del jugador
                 self.image = pygame.transform.flip(self.image, True, False) # Flip horizontal
        except pygame.error:
            # Fallback
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED) 
            
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(self.rect.center)
        
    def update(self):
        """Mueve al enemigo hacia el jugador."""
        
        target_pos = pygame.math.Vector2(self.target.rect.center)
        direction = target_pos - self.pos # Vector de la posición del enemigo al jugador
        
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
            self.rect.center = (int(self.pos.x), int(self.pos.y))
            
    def take_damage(self, amount):
        """Reduce la vida y devuelve True si el enemigo muere."""
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True
        return False
        
    def draw_health_bar(self, surface, offset): # <--- CORREGIDO: RECIBE Y USA EL OFFSET
        """Dibuja una simple barra de vida sobre el enemigo."""
        bar_w = TILE_SIZE * 0.8
        bar_h = 5
        
        # Aplica el offset de la cámara para la posición de dibujo
        draw_x = self.rect.centerx - bar_w // 2 - offset.x # <--- APLICAR offset.x
        draw_y = self.rect.top - 10 - offset.y # <--- APLICAR offset.y
        
        # DIBUJAR BARRA
        fill = (self.health / self.max_health) * bar_w 
        
        outline_rect = pygame.Rect(draw_x, draw_y, bar_w, bar_h)
        fill_rect = pygame.Rect(draw_x, draw_y, fill, bar_h)
        
        pygame.draw.rect(surface, RED, outline_rect) # Fondo de la barra (rojo)
        pygame.draw.rect(surface, GREEN, fill_rect)  # Relleno de la barra (verde)
        pygame.draw.rect(surface, WHITE, outline_rect, 1) # Borde blanco