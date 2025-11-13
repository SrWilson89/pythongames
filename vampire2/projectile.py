# projectile.py - VERSIÓN CORREGIDA
import pygame
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


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, damage, groups, lifetime=120): # Añadido lifetime
        super().__init__(groups)
        
        # 1. Configuración Visual (Carga del PNG y ESCALADO)
        SPRITE_W = TILE_SIZE  
        SPRITE_H = TILE_SIZE // 2 
        
        try:
            # Usa resource_path para la carga
            original_image = pygame.image.load(resource_path("assets/sprites/dagger.png")).convert_alpha() 
            self.image = pygame.transform.scale(original_image, (SPRITE_W, SPRITE_H))
            
            # Rotar la imagen para que apunte en la dirección
            # Rotamos la imagen de forma que apunte hacia el vector (1, 0)
            angle = pygame.math.Vector2(direction_vector).angle_to(pygame.math.Vector2(1, 0))
            self.image = pygame.transform.rotate(self.image, angle) 
            
        except pygame.error:
            # Fallback
            self.image = pygame.Surface((SPRITE_W, SPRITE_H)) 
            self.image.fill((255, 255, 255))
            
        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Estadísticas
        self.damage = damage
        self.speed = 10 
        self.lifetime = lifetime # En frames (ahora usa el parámetro de la habilidad)
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
        # La daga solo golpea una vez
        hit_list = pygame.sprite.spritecollide(self, enemies_group, False)
        if hit_list:
            enemy = hit_list[0]
            if enemy.take_damage(self.damage):
                 from experience_orb import ExperienceOrb
                 ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs_group,))
            self.kill() # La daga se elimina al golpear