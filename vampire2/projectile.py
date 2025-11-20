# projectile.py
import pygame
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

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, direction_vector, damage, groups, lifetime=120):
        super().__init__(groups)
        
        # 1. Configuración Visual (Usando resource_path)
        SPRITE_W = TILE_SIZE  
        SPRITE_H = TILE_SIZE // 2 
        
        try:
            original_image = pygame.image.load(resource_path("assets/sprites/dagger.png")).convert_alpha() 
            self.image = pygame.transform.scale(original_image, (SPRITE_W, SPRITE_H))
            
            # Rotar la imagen para que apunte en la dirección
            angle = pygame.math.Vector2(direction_vector).angle_to(pygame.math.Vector2(1, 0))
            self.image = pygame.transform.rotate(self.image, angle) 
            
        except pygame.error:
            self.image = pygame.Surface((SPRITE_W, SPRITE_H)) 
            self.image.fill((255, 255, 255))
            
        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Estadísticas
        self.damage = damage
        self.speed = 10 
        self.lifetime = lifetime
        self.timer = 0
        
        # 3. Movimiento
        self.direction = direction_vector
        self.pos = pygame.math.Vector2(self.rect.center)
        
    def update(self):
        self.timer += 1
        
        # Movimiento
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # Eliminar si expira
        if self.timer >= self.lifetime:
            self.kill()