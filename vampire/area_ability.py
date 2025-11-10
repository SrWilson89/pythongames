# area_ability.py
import pygame
import math
from config import TILE_SIZE

class AreaAbility(pygame.sprite.Sprite):
    def __init__(self, player, damage, radius_multiplier, cooldown, groups, ability_type="fire"):
        super().__init__(groups)
        self.player = player
        self.damage = damage
        self.radius_multiplier = radius_multiplier
        self.cooldown = cooldown
        self.ability_type = ability_type

        # RADIO BASE
        self.base_radius = int(TILE_SIZE * 3 * radius_multiplier)
        self.damage_radius = self.base_radius

        # CARGAR TU PNG PERSONALIZADO
        try:
            original = pygame.image.load("assets/sprites/fire_ring.png").convert_alpha()
            self.original_image = pygame.transform.scale(original, (self.base_radius * 2, self.base_radius * 2))
        except pygame.error as e:
            print(f"ERROR: fire_ring.png no encontrado → {e}")
            self.original_image = pygame.Surface((self.base_radius * 2, self.base_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 100, 0, 100), (self.base_radius, self.base_radius), self.base_radius, 8)

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=player.rect.center)
        self.last_damage_time = 0
        self.rotation = 0  # Para efecto de rotación

    def update(self):
        self.rect.center = self.player.rect.center
        self.rotation = (self.rotation + 1) % 360  # Rotación lenta
        self.image = pygame.transform.rotate(self.original_image, self.rotation)
        self.rect = self.image.get_rect(center=self.player.rect.center)

    def draw_custom(self, surface):
        if self.ability_type == "fire":
            # PULSO DE TAMAÑO
            pulse = 0.95 + 0.05 * math.sin(pygame.time.get_ticks() * 0.008)
            current_size = int(self.base_radius * 2 * pulse)
            
            # Escalar imagen con pulso
            scaled = pygame.transform.scale(self.original_image, (current_size, current_size))
            rotated = pygame.transform.rotate(scaled, self.rotation)
            rect = rotated.get_rect(center=self.player.rect.center)
            
            # Dibujar con transparencia pulsante
            alpha = int(180 + 75 * math.sin(pygame.time.get_ticks() * 0.01))
            rotated.set_alpha(alpha)
            
            surface.blit(rotated, rect.topleft)