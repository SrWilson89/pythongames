# bumerang.py

import pygame
import math
import random
from config import TILE_SIZE

class Bumerang(pygame.sprite.Sprite): 
    def __init__(self, player, damage, speed, lifetime, groups):
        super().__init__(groups)
        
        self.player = player
        self.damage = damage
        self.speed = speed
        self.lifetime_max = lifetime
        
        # 1. Configuración Visual (Carga del PNG y ESCALADO)
        SPRITE_SIZE = TILE_SIZE 

        try:
            original_image = pygame.image.load("assets/sprites/bumerang.png").convert_alpha()
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
        # Dirección inicial (aleatoria para variabilidad)
        angle = random.uniform(0, 2 * math.pi)
        self.direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        
        self.timer = 0
        self.returning = False
        self.rotation_angle = 0
        self.has_hit = False # <--- CORRECCIÓN: Inicializa la bandera de golpeo
        
    def update(self):
        """Mueve el bumerán, lo hace regresar y comprueba el tiempo de vida."""
        
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
                self.timer = 0 # Reiniciar el timer si se quiere limitar la fase de regreso
                self.has_hit = False # <--- IMPORTANTE: Reiniciar has_hit para la fase de vuelta
                
        else:
            # Fase 2: Regresar
            player_pos = pygame.math.Vector2(self.player.rect.center)
            to_player = player_pos - self.pos
            
            if to_player.length_squared() > 0:
                # Normalizar la dirección hacia el jugador
                to_player = to_player.normalize()
                self.pos += to_player * self.speed
                
                # Comprobar si ha llegado al jugador
                if self.pos.distance_to(player_pos) < TILE_SIZE / 2: 
                    self.kill() # Eliminar al volver
            else:
                 self.kill() # Eliminar si está exactamente encima del jugador
            
        self.rect.center = (int(self.pos.x), int(self.pos.y))