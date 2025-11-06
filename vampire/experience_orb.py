# experience_orb.py
import pygame
from config import TILE_SIZE, BLUE

class ExperienceOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, groups):
        super().__init__(groups)
        self.amount = amount
        self.size = TILE_SIZE // 4 # Pequeño
        
        self.image = pygame.Surface((self.size, self.size))
        self.image.fill(BLUE) 
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        # Lógica de movimiento hacia el jugador cuando está cerca (a implementar)
        pass