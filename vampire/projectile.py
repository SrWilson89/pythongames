# projectile.py

import pygame
from config import TILE_SIZE

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, damage, groups):
        super().__init__(groups)
        
        # 1. Configuración Visual (Carga del PNG y ESCALADO)
        SPRITE_W = TILE_SIZE  
        SPRITE_H = TILE_SIZE // 2 
        
        try:
            original_image = pygame.image.load("assets/sprites/dagger.png").convert_alpha() 
            self.image = pygame.transform.scale(original_image, (SPRITE_W, SPRITE_H))
            
            # Rotar la imagen para que apunte en la dirección
            # Rotamos la imagen de forma que apunte hacia el vector (1, 0)
            angle = pygame.math.Vector2(direction_vector).angle_to(pygame.math.Vector2(1, 0))
            self.image = pygame.transform.rotate(self.image, angle) 
            
        except pygame.error:
            self.image = pygame.Surface((SPRITE_W, SPRITE_H)) 
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