# bomb.py
import pygame
import random
import os 
import sys 
from config import TILE_SIZE

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA
# =======================================================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
# =======================================================

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, radius_multiplier, fall_time, groups, orbs_group):
        super().__init__(groups)
        
        self.damage = damage
        self.fall_time = fall_time
        self.radius_multiplier = radius_multiplier
        self.orbs_group = orbs_group
        
        self.timer = 0
        self.exploded = False
        self.target_enemies = groups 
        
        # Posición y Radio
        self.pos = pygame.math.Vector2(x, y)
        self.base_radius = TILE_SIZE * 1.5
        self.explosion_radius = int(self.base_radius * self.radius_multiplier)
        self.current_radius = TILE_SIZE // 4
        
        # Visual (Usando resource_path)
        try:
            grenade_path = resource_path("assets/sprites/granade.png")
            original = pygame.image.load(grenade_path).convert_alpha()
            size = (TILE_SIZE // 2, TILE_SIZE // 2)
            self.original_image = pygame.transform.scale(original, size)
            self.image = self.original_image.copy()
        except pygame.error as e:
            self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 0, 0), (TILE_SIZE // 4, TILE_SIZE // 4), TILE_SIZE // 4)
            
        self.rect = self.image.get_rect(center=self.pos)
        self.shadow_rect = self.rect.copy()

    def update(self):
        # ... (Lógica de caída y explosión) ...
        self.timer += 1
        if self.exploded:
            if self.timer > 10:
                self.kill() # Eliminar después del flash de explosión
            return
            
        # Animación de Caída
        if self.timer <= self.fall_time:
            progress = self.timer / self.fall_time
            # El radio visual crece
            self.current_radius = int((TILE_SIZE // 4) + (self.base_radius * 0.5 - TILE_SIZE // 4) * progress)
            size = (self.current_radius * 2, self.current_radius * 2)
            self.image = pygame.transform.scale(self.original_image, size)
            self.rect = self.image.get_rect(center=self.pos)
            
        else:
            self.explode()

    def explode(self):
        if self.exploded: return
        self.exploded = True
        self.timer = 0 # Reiniciar el timer para la animación de flash

        # === GENERAR DAÑO ===
        hit_enemies = []
        for sprite in self.target_enemies.sprites():
            if (sprite != self and 
                sprite.__class__.__name__ == 'Enemy' and 
                self.pos.distance_to(sprite.pos) < self.explosion_radius):
                hit_enemies.append(sprite)

        # === GENERAR ORBES ===
        from experience_orb import ExperienceOrb
        for enemy in hit_enemies:
            if enemy.take_damage(self.damage):
                ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (self.orbs_group,))

        # === EXPLOSIÓN VISUAL (Rectángulo de colisión actualizado para el flash) ===
        self.image = pygame.Surface((self.explosion_radius * 3, self.explosion_radius * 3), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)

    def draw_custom(self, surface, offset): # <--- CORRECCIÓN CLAVE
        if not self.exploded:
            # Dibuja la sombra
            shadow_radius = self.current_radius * 0.6
            
            # Posición de la sombra APLICANDO EL OFFSET
            shadow_center_x = int(self.rect.centerx - offset.x)
            shadow_center_y = int(self.rect.bottom - 5 - offset.y)
            
            pygame.draw.circle(surface, (0, 0, 0, 80), 
                             (shadow_center_x, shadow_center_y), 
                             int(shadow_radius))
            
            # Dibuja la bomba APLICANDO EL OFFSET
            surface.blit(self.image, self.rect.move(-offset.x, -offset.y))
        else:
            # Animación de flash de la explosión
            alpha = max(0, 255 - int(255 * (self.timer / 10)))
            color = (255, 180, 0, alpha)
            
            # Dibujar un círculo blanco/amarillo pulsante
            radius = self.explosion_radius * (1 + self.timer / 10)
            
            temp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp, color, (radius, radius), radius)
            
            # Dibujar la explosión APLICANDO EL OFFSET
            temp_rect = temp.get_rect(center=(self.rect.centerx - offset.x, self.rect.centery - offset.y))
            surface.blit(temp, temp_rect)