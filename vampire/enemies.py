# enemies.py
import pygame
import math
from config import TILE_SIZE, RED, WHITE

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, target, groups):
        super().__init__(groups)
        
        self.target = target
        self.health = 10
        self.speed = 1.5 
        
        # Carga y escala el sprite del enemigo
        try:
            original_image = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED) # Fallback rojo
            
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
        self.health -= amount
        if self.health <= 0:
            self.kill()
            return True # Retorna True si muere
        return False