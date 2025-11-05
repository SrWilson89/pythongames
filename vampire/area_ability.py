# area_ability.py

import pygame
from config import RED, BLACK

class AreaAbility(pygame.sprite.Sprite):
    def __init__(self, player, ability_id, damage, radius, cooldown, groups):
        super().__init__(groups)
        
        self.player = player
        self.ability_id = ability_id
        self.damage = damage
        self.radius = radius
        self.cooldown = cooldown 
        
        self.last_damage_tick = pygame.time.get_ticks()
        
        self._update_visuals()

    def _update_visuals(self):
        """Redibuja el círculo si el radio ha cambiado, asegurando el centro."""
        diameter = self.radius * 2
        self.image = pygame.Surface((diameter, diameter), pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0)) 
        
        # Opacidad del Aura aumentada a 150 (de 100)
        pygame.draw.circle(self.image, (255, 0, 0, 150), (self.radius, self.radius), self.radius) 
        
        self.rect = self.image.get_rect(center=self.player.rect.center)
        self.radius_for_collision = self.radius 

    def update(self, enemies):
        """Sigue al jugador y aplica daño a los enemigos en rango."""
        
        if self.rect.width != self.radius * 2:
            self._update_visuals()

        self.rect.center = self.player.rect.center
        
        current_time = pygame.time.get_ticks()

        if current_time - self.last_damage_tick > self.cooldown:
            self.last_damage_tick = current_time
            
            hit_enemies = pygame.sprite.spritecollide(self, enemies, False, pygame.sprite.collide_circle)
            
            for enemy in hit_enemies:
                enemy.take_damage(self.damage)