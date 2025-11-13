# bumerang.py - VERSIÓN CORREGIDA

import pygame
import math
import random
import os 
import sys 
from config import TILE_SIZE

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA (Añadida para PyInstaller)
# =======================================================
def resource_path(relative_path):
    """
    Función que maneja rutas de recursos para desarrollo local o
    ejecutables empaquetados por PyInstaller.
    """
    try:
        # sys._MEIPASS es la ruta de la carpeta temporal que PyInstaller crea
        base_path = sys._MEIPASS
    except Exception:
        # Si no está empaquetado (se ejecuta localmente), usa la ruta actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# =======================================================

class Bumerang(pygame.sprite.Sprite): 
    def __init__(self, player, damage, speed, lifetime, groups):
        super().__init__(groups)
        
        self.player = player
        self.damage = damage
        self.speed = speed
        self.lifetime_max = lifetime # Duración de la fase de ida (en frames)
        
        # 1. Configuración Visual (Carga del PNG y ESCALADO)
        SPRITE_SIZE = TILE_SIZE 

        try:
            # Usa resource_path para la carga
            original_image = pygame.image.load(resource_path("assets/sprites/bumerang.png")).convert_alpha()
            self.image = pygame.transform.scale(original_image, (SPRITE_SIZE, SPRITE_SIZE))
            self.original_image = self.image.copy() # Copia para rotación
        except pygame.error:
            # Fallback
            self.image = pygame.Surface((SPRITE_SIZE, SPRITE_SIZE), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0))
            pygame.draw.rect(self.image, (255, 255, 0), (0, 0, SPRITE_SIZE, SPRITE_SIZE))
            self.original_image = self.image.copy()
            
        self.rect = self.image.get_rect(center=player.rect.center)
        
        # 2. Lógica de Movimiento
        self.pos = pygame.math.Vector2(self.rect.center)
        self.direction = player.last_move_direction if player.last_move_direction.length_squared() > 0 else pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
        self.timer = 0
        self.returning = False
        self.has_hit = False # Para saber si golpeó en la fase de ida o vuelta
        self.rotation_angle = 0 # Para rotación visual
        
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
                self.has_hit = False # IMPORTANTE: Reiniciar has_hit para la fase de vuelta
                
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
                 self.kill() # Si no hay distancia (está en el jugador), eliminar

        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def check_hit(self, enemies_group):
        """Revisa colisiones con enemigos y si golpea, establece la bandera has_hit=True."""
        # Solo chequea la colisión si no ha golpeado en la fase actual
        if not self.has_hit:
            hit_list = pygame.sprite.spritecollide(self, enemies_group, False)
            if hit_list:
                enemy = hit_list[0] # Solo golpea al primero en la lista
                if enemy.take_damage(self.damage):
                    # Generar orbe, si es necesario, debería ser manejado por la clase que llama a check_hit
                    pass
                self.has_hit = True # Impide que golpee a más enemigos en esta fase (ida o vuelta)