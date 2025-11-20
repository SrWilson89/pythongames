# bumerang.py
import pygame
import math
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

class Bumerang(pygame.sprite.Sprite): 
    def __init__(self, player, damage, speed, lifetime, groups):
        super().__init__(groups)
        
        self.player = player
        self.damage = damage
        self.speed = speed
        self.lifetime_max = lifetime
        
        # 1. Configuración Visual (Usando resource_path)
        SPRITE_SIZE = TILE_SIZE 

        try:
            original_image = pygame.image.load(resource_path("assets/sprites/bumerang.png")).convert_alpha()
            self.image = pygame.transform.scale(original_image, (SPRITE_SIZE, SPRITE_SIZE))
            self.original_image = self.image.copy() # Copia para rotación
        except pygame.error:
            self.image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, (255, 255, 0), (0, 0, SPRITE_SIZE, SPRITE_SIZE))
            self.original_image = self.image.copy()
            
        self.rect = self.image.get_rect(center=player.rect.center)
        
        # 2. Lógica de Movimiento
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        self.returning = False 
        self.timer = 0
        self.has_hit = False # Solo puede golpear una vez por fase (ida o vuelta)
        self.rotation_angle = 0
        
    def update(self):
        self.timer += 1
        
        # Rotación para efecto visual
        self.rotation_angle = (self.rotation_angle + 10) % 360
        original_center = self.rect.center
        self.image = pygame.transform.rotate(self.original_image, self.rotation_angle)
        self.rect = self.image.get_rect(center=original_center)


        if not self.returning:
            # Fase 1: Ir
            self.pos += self.direction * self.speed
            
            if self.timer >= self.lifetime_max:
                self.returning = True
                self.timer = 0
                self.has_hit = False
                
        else:
            # Fase 2: Regresar
            player_pos = pygame.math.Vector2(self.player.rect.center)
            to_player = player_pos - self.pos
            
            if to_player.length_squared() > 0:
                to_player = to_player.normalize()
                self.pos += to_player * self.speed
                
                # Comprobar si ha llegado al jugador
                if self.pos.distance_to(player_pos) < TILE_SIZE / 2: 
                    self.kill()
            else:
                 self.kill()

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def check_hit(self, enemies_group):
        hit_list = pygame.sprite.spritecollide(self, enemies_group, False)
        if hit_list and not self.has_hit:
            self.has_hit = True
            enemy = hit_list[0]
            return [enemy]
        return []