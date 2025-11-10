# bomb.py
import pygame
import random
from config import TILE_SIZE

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, radius_multiplier, fall_time, groups, orbs_group):
        super().__init__(groups)
        
        self.damage = damage
        self.fall_time = fall_time
        self.radius_multiplier = radius_multiplier
        self.orbs_group = orbs_group
        
        self.timer = 0
        self.exploded = False
        
        # Visual
        self.base_radius = TILE_SIZE * 1.5
        self.explosion_radius = int(self.base_radius * self.radius_multiplier)
        self.current_radius = TILE_SIZE // 4
        
        try:
            grenade_path = "assets/sprites/granade.png"
            original = pygame.image.load(grenade_path).convert_alpha()
            size = (TILE_SIZE // 2, TILE_SIZE // 2)
            self.original_image = pygame.transform.scale(original, size)
            self.image = self.original_image.copy()
        except pygame.error as e:
            print(f"ERROR granade.png: {e}")
            self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 100, 50), (TILE_SIZE // 4, TILE_SIZE // 4), TILE_SIZE // 4)
        
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(self.rect.center)

    def update(self):
        self.timer += 1
        
        if not self.exploded:
            if self.timer > self.fall_time * 0.7:
                if self.timer % 4 < 2:
                    flash = self.original_image.copy()
                    overlay = pygame.Surface(flash.get_size(), pygame.SRCALPHA)
                    overlay.fill((255, 50, 50, 150))
                    flash.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)
                    self.image = flash
            
            if self.timer >= self.fall_time:
                self.explode()
                
        elif self.exploded:
            self.current_radius += 12
            if self.current_radius > self.explosion_radius * 1.5:
                self.kill()

    def explode(self):
        self.exploded = True
        self.timer = 0
        
        # === BUSCAR ENEMIGOS EN CUALQUIER GRUPO (sin usar 'bombs') ===
        hit_enemies = []
        for group in self.groups():
            for sprite in group:
                # Filtrar: tiene pos, take_damage, y NO es una bomba
                if (hasattr(sprite, 'pos') and 
                    hasattr(sprite, 'take_damage') and 
                    sprite.__class__.__name__ != 'Bomb' and  # Excluir bombas
                    self.pos.distance_to(sprite.pos) < self.explosion_radius):
                    hit_enemies.append(sprite)

        # === GENERAR ORBES ===
        from experience_orb import ExperienceOrb
        for enemy in hit_enemies:
            if enemy.take_damage(self.damage):
                ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (self.orbs_group,))

        # === EXPLOSIÓN VISUAL ===
        self.image = pygame.Surface((self.explosion_radius * 3, self.explosion_radius * 3), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.pos)

    def draw_custom(self, surface):
        if not self.exploded:
            shadow_radius = self.current_radius * 0.6
            pygame.draw.circle(surface, (0, 0, 0, 80), 
                             (int(self.rect.centerx), int(self.rect.bottom - 5)), 
                             int(shadow_radius))
            surface.blit(self.image, self.rect)
        else:
            alpha = max(0, 255 - int(255 * (self.current_radius / (self.explosion_radius * 1.5))))
            color = (255, 180 - alpha//3, 0, alpha)
            temp = pygame.Surface((self.current_radius * 2, self.current_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp, color, (int(self.current_radius), int(self.current_radius)), int(self.current_radius))
            surface.blit(temp, (int(self.pos.x - self.current_radius), int(self.pos.y - self.current_radius)))