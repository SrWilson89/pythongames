# enemies.py
import pygame
import math
import random 
from config import TILE_SIZE, RED, WHITE, GREEN

# Lista de sprites de enemigos disponibles (incluyendo enemy.png, enemy1.png, enemy2.png)
ENEMY_SPRITES = ["enemy.png", "enemy1.png", "enemy2.png", "enemy3.png", "enemy4.png", "enemy5.png", "enemy6.png", "enemy7.png", "enemy8.png", "enemy9.png", "enemy10.png", "enemy11.png", "enemy12.png"] 

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target, groups, health_multiplier=1.0):
        super().__init__(groups)
        
        self.target = target
        
        # --- Lógica de Salud con Multiplicador ---
        base_health = 10
        self.health = base_health * health_multiplier 
        self.max_health = base_health * health_multiplier
        self.speed = 1.5 
        
        # --- LÓGICA DE SPRITE ALEATORIO ---
        chosen_sprite = random.choice(ENEMY_SPRITES)
        sprite_path = f"assets/sprites/{chosen_sprite}"
        
        # Carga y escala el sprite del enemigo
        try:
            original_image = pygame.image.load(sprite_path).convert_alpha() 
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            # Fallback en caso de que no encuentre el archivo
            print(f"ERROR: No se pudo cargar el sprite {sprite_path}. {e}")
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
        
    def draw_health_bar(self, surface):
        """Dibuja una simple barra de vida sobre el enemigo."""
        bar_w = TILE_SIZE * 0.8
        bar_h = 5
        
        # USA self.max_health para la proporción
        fill = (self.health / self.max_health) * bar_w 
        
        outline_rect = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - 10, bar_w, bar_h)
        fill_rect = pygame.Rect(self.rect.centerx - bar_w // 2, self.rect.top - 10, fill, bar_h)
        
        pygame.draw.rect(surface, RED, outline_rect)
        pygame.draw.rect(surface, GREEN, fill_rect)
        pygame.draw.rect(surface, WHITE, outline_rect, 1)