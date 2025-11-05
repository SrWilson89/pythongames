# projectile.py

import pygame
from config import TILE_SIZE

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, damage, groups):
        super().__init__(groups)
        
        # 1. Configuración Visual (Carga del PNG)
        try:
            # CARGAMOS EL SPRITE DE LA DAGA
            self.image = pygame.image.load("assets/sprites/dagger.png").convert_alpha() 
            # Re-escalamos al tamaño del sprite original
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE // 2)) 
        except pygame.error:
            # Fallback a un rectángulo blanco si no se encuentra el PNG
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE // 2)) 
            self.image.fill((255, 255, 255))
            
        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Estadísticas
        self.damage = damage
        self.speed = 10 
        self.lifetime = 120 
        self.timer = 0
        
        # 3. Movimiento
        self.direction = direction_vector
        self.pos = pygame.math.Vector2(self.rect.center) 

    def update(self):
        """Mueve el proyectil y comprueba su tiempo de vida."""
        
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        self.timer += 1
        if self.timer >= self.lifetime:
            self.kill()