# experience_orb.py

import pygame
from config import TILE_SIZE, GREEN

class ExperienceOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, value, groups):
        super().__init__(groups) 
        
        self.value = value 
        
        # Tamaño y apariencia
        size = TILE_SIZE // 4
        self.image = pygame.Surface((size, size), pygame.SRCALPHA)
        pygame.draw.circle(self.image, GREEN, (size // 2, size // 2), size // 2)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(x, y)
        self.magnet_range = 100 
        self.speed = 4
        
    def update(self, player):
        """Mueve el orbe hacia el jugador si está cerca."""
        
        player_pos = pygame.math.Vector2(player.rect.center)
        distance = self.pos.distance_to(player_pos)
        
        if distance < self.magnet_range:
            # Vector de dirección hacia el jugador
            direction = (player_pos - self.pos).normalize()
            
            self.pos += direction * self.speed
            self.rect.center = (int(self.pos.x), int(self.pos.y))