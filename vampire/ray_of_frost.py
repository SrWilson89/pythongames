# ray_of_frost.py
import pygame
import math
from config import TILE_SIZE

class RayOfFrost(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, damage, groups):
        super().__init__(groups)
        
        # 1. Configuración Visual (Carga del PNG y ESCALADO)
        SPRITE_W = TILE_SIZE  
        SPRITE_H = TILE_SIZE 
        
        try:
            # Intentamos cargar la imagen 'ice_shard.png'
            original_image = pygame.image.load("assets/sprites/ice_shard.png").convert_alpha() 
            self.image = pygame.transform.scale(original_image, (SPRITE_W, SPRITE_H))
            
            # Rotar la imagen para que apunte en la dirección
            # Rotamos en base al vector (1, 0)
            angle = pygame.math.Vector2(direction_vector).angle_to(pygame.math.Vector2(1, 0))
            self.image = pygame.transform.rotate(self.image, angle) 
            
        except pygame.error:
            # Fallback al emoji si el PNG no se encuentra
            self.font = pygame.font.Font(None, SPRITE_W)
            self.image = self.font.render("❄️", True, (0, 150, 255)) 

        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Estadísticas
        self.damage = damage
        self.speed = 8  
        self.lifetime = 150 # En frames
        self.timer = 0
        
        # 3. Movimiento
        self.direction = direction_vector
        self.pos = pygame.math.Vector2(self.rect.center)
        
    def update(self):
        """Mueve el proyectil y lo elimina tras su tiempo de vida."""
        
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        self.timer += 1
        if self.timer >= self.lifetime:
            self.kill()