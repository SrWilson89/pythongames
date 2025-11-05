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
        
        # 1. Configuración Visual (Carga del PNG)
        try:
            # CARGAMOS EL SPRITE DEL BUMERÁN
            self.image = pygame.image.load("assets/sprites/bumerang.png").convert_alpha()
            # Re-escalamos al tamaño del sprite original
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            # Fallback a un cuadrado amarillo si no se encuentra el PNG
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, (255, 255, 0), (0, 0, TILE_SIZE, TILE_SIZE))
            
        self.rect = self.image.get_rect(center=player.rect.center)
        
        # 2. Lógica de Movimiento (se mantiene igual)
        self.pos = pygame.math.Vector2(self.rect.center)
        angle = random.uniform(0, 2 * math.pi)
        self.direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
        
        self.timer = 0
        self.returning = False
        
    def update(self):
        """Mueve el bumerán, lo hace regresar y comprueba el tiempo de vida."""
        
        self.timer += 1

        if not self.returning:
            # Fase 1: Ir
            self.pos += self.direction * self.speed
            
            if self.timer >= self.lifetime_max:
                self.returning = True
                self.timer = 0 
                
        else:
            # Fase 2: Regresar
            player_pos = pygame.math.Vector2(self.player.rect.center)
            to_player = player_pos - self.pos
            
            if to_player.length() > self.speed:
                self.direction = to_player.normalize()
                self.pos += self.direction * self.speed
            else:
                self.kill()
        
        self.rect.center = (int(self.pos.x), int(self.pos.y))