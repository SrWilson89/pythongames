# area_ability.py
import pygame
from config import RED, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

class AreaAbility(pygame.sprite.Sprite):
    def __init__(self, player, damage, radius, cooldown, groups):
        super().__init__(groups)
        self.player = player
        self.damage = damage
        self.cooldown = cooldown
        self.radius = radius * (TILE_SIZE // 32) # Escalar el radio según TILE_SIZE
        
        # Se dibuja dinámicamente, no necesita imagen fija
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.player.rect.center)
        
        self.last_damage_time = 0

    def update(self):
        """Actualiza la posición y aplica daño en el tiempo."""
        self.rect.center = self.player.rect.center
        
        # Dibuja un aura roja semi-transparente
        self.image.fill((0, 0, 0, 0)) # Limpiar
        aura_color = (255, 100, 0, 100) # Naranja/Rojo semi-transparente
        pygame.draw.circle(self.image, aura_color, (self.radius, self.radius), self.radius)
        
        # Lógica de daño
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.cooldown:
            # Aquí iría la lógica para encontrar y dañar enemigos dentro del radio
            # self.apply_damage()
            self.last_damage_time = current_time