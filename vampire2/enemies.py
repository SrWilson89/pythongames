# enemies.py
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
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# =======================================================

# Lista de sprites de enemigos disponibles (incluyendo enemy.png, enemy1.png, etc.)
ENEMY_SPRITES = [
    "enemy.png", "enemy1.png", "enemy2.png", "enemy3.png", "enemy4.png", 
    "enemy5.png", "enemy6.png", "enemy7.png", "enemy8.png", "enemy9.png", 
    "enemy10.png", "enemy11.png", "enemy12.png"
] 

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target, groups, orbs_group, health_multiplier=1.0): # AÑADIDO orbs_group
        super().__init__(groups)
        
        self.target = target
        self.orbs_group = orbs_group # Guardar el grupo de orbes para la muerte
        
        # --- Lógica de Salud con Multiplicador ---
        base_health = 10
        self.health = base_health * health_multiplier 
        self.max_health = base_health * health_multiplier
        self.speed = 1.5 
        
        # --- LÓGICA DE SPRITE ALEATORIO ---
        chosen_sprite = random.choice(ENEMY_SPRITES)
        sprite_path = resource_path(f"assets/sprites/{chosen_sprite}") # CORRECCIÓN: USAR resource_path
        
        # Carga y escala el sprite del enemigo
        try:
            original_image = pygame.image.load(sprite_path).convert_alpha() 
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            # Fallback
            print(f"Advertencia: No se pudo cargar {chosen_sprite}. Usando cuadrado rojo. Error: {e}")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED) 
            
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(self.rect.center)
        
    def update(self):
        """Mueve al enemigo hacia el jugador."""
        
        target_pos = pygame.math.Vector2(self.target.rect.center)
        direction = target_pos - self.pos
        
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
        
    def draw_health_bar(self, surface, offset): # <--- CORRECCIÓN CLAVE: RECIBE EL OFFSET
        """Dibuja una simple barra de vida sobre el enemigo."""
        bar_w = TILE_SIZE * 0.8
        bar_h = 5
        
        # Aplica el offset de la cámara
        draw_x = self.rect.centerx - bar_w // 2 - offset.x # <--- APLICAR offset.x
        draw_y = self.rect.top - 10 - offset.y # <--- APLICAR offset.y
        
        # DIBUJAR BARRA
        fill = (self.health / self.max_health) * bar_w 
        
        outline_rect = pygame.Rect(draw_x, draw_y, bar_w, bar_h)
        fill_rect = pygame.Rect(draw_x, draw_y, fill, bar_h)
        
        pygame.draw.rect(surface, RED, outline_rect, 1) # Borde
        pygame.draw.rect(surface, GREEN, fill_rect) # Relleno