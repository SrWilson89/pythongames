# experience_orb.py
import pygame
import math
from config import TILE_SIZE, SCREEN_HEIGHT, GREEN, WHITE  # ¡AÑADIDO SCREEN_HEIGHT!

class ExperienceOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, groups):
        super().__init__(groups)
        
        self.amount = amount
        self.size = TILE_SIZE * 0.8  # ¡ORBES GRANDES!
        
        # Posición
        self.pos = pygame.math.Vector2(x, y)
        
        # Lógica de recolección
        self.target = None
        self.speed = 4.0
        self.collection_radius = TILE_SIZE * 3
        self.is_magnetized = False

        # Visual
        try:
            original_image = pygame.image.load("assets/sprites/experience_orb.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (self.size, self.size))
        except pygame.error:
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, GREEN, (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 2, 3)
            pygame.draw.circle(self.image, (255, 255, 0), (self.size // 2, self.size // 2), self.size // 3, 2)
        
        self.rect = self.image.get_rect(center=(x, y))

    def set_target(self, player, magnetism_aura_radius=1.0):
        self.target = player
        effective_radius = self.collection_radius * player.level * magnetism_aura_radius
        distance = self.pos.distance_to(player.pos)
        if distance < effective_radius:
            self.is_magnetized = True

    def update(self):
        if self.target and self.is_magnetized:
            direction = self.target.pos - self.pos
            if direction.length_squared() > 0:
                direction = direction.normalize()
                self.pos += direction * self.speed
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                
                if self.pos.distance_to(self.target.pos) < TILE_SIZE // 4:
                    self.kill()
        else:
            self.pos.y += 1.5
            self.rect.centery = int(self.pos.y)
            
            # ¡AHORA FUNCIONA! Usa SCREEN_HEIGHT del config
            if self.rect.bottom > SCREEN_HEIGHT + 100:
                self.kill()