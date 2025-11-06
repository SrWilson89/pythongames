# ray_of_frost.py (EJEMPLO)
import pygame
import math
from config import TILE_SIZE

class RayOfFrost(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, damage, groups):
        super().__init__(groups)
        
        # ... Inicialización de daño, velocidad, etc. ...

        # Configuración visual con emoji de copo de nieve
        self.font = pygame.font.Font(None, TILE_SIZE) 
        self.image = self.font.render("❄️", True, (0, 150, 255))
        self.rect = self.image.get_rect(center=(x, y))
        
        # ... Lógica de movimiento como Projectile ...