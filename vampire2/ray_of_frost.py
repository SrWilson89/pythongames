# ray_of_frost.py - VERSIÓN CORREGIDA
import pygame
import math
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

class RayOfFrost(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, damage, groups):
        super().__init__(groups)
        
        # 1. Configuración Visual (Carga del PNG y ESCALADO)
        SPRITE_W = TILE_SIZE  
        SPRITE_H = TILE_SIZE 
        
        try:
            # Intentamos cargar la imagen 'ice_shard.png' usando resource_path
            original_image = pygame.image.load(resource_path("assets/sprites/ice_shard.png")).convert_alpha() 
            self.image = pygame.transform.scale(original_image, (SPRITE_W, SPRITE_H))
            
            # Rotar la imagen para que apunte en la dirección
            # Rotamos en base al vector (1, 0)
            angle = pygame.math.Vector2(direction_vector).angle_to(pygame.math.Vector2(1, 0))
            self.image = pygame.transform.rotate(self.image, angle) 
            
        except pygame.error:
            # Fallback al emoji si el PNG no se encuentra
            self.font = pygame.font.Font(None, SPRITE_W)
            self.image = self.font.render("❄️", True, (0, 150, 255)) 

        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Estadísticas
        self.damage = damage
        self.speed = 8  
        self.lifetime = 150 # En frames
        self.timer = 0
        
        # 3. Movimiento
        self.direction = direction_vector
        self.pos = pygame.math.Vector2(self.rect.center)
        
    def update(self):
        self.timer += 1
        
        # Movimiento
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        if self.timer > self.lifetime:
            self.kill()
            
    def check_hit(self, enemies_group, orbs_group):
        # Rayos de escarcha solo golpean una vez
        hit_list = pygame.sprite.spritecollide(self, enemies_group, False)
        if hit_list:
            enemy = hit_list[0]
            if enemy.take_damage(self.damage):
                 from experience_orb import ExperienceOrb
                 ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs_group,))
            self.kill() # Se elimina al golpear