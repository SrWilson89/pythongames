# experience_orb.py - VERSIÓN CORREGIDA
import pygame
import math
import os 
import sys 
from config import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, WHITE  # <--- CORREGIDO: AÑADIDO SCREEN_WIDTH

# ... (El resto del código con resource_path que ya habías añadido debe estar)

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

class ExperienceOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, groups):
        super().__init__(groups)
        
        self.amount = amount
        self.size = TILE_SIZE * 0.8  # ¡ORBES GRANDES!
        
        # Posición
        self.pos = pygame.math.Vector2(x, y)
        
        # Lógica de recolección
        self.target = None
        self.speed = 4.0
        self.collection_radius = TILE_SIZE * 3
        self.is_magnetized = False

        # Visual
        try:
            # Usa resource_path para la carga
            original_image = pygame.image.load(resource_path("assets/sprites/experience_orb.png")).convert_alpha()
            self.image = pygame.transform.scale(original_image, (self.size, self.size))
        except pygame.error:
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, GREEN, (self.size // 2, self.size // 2), self.size // 2)
            pygame.draw.circle(self.image, WHITE, (self.size // 2, self.size // 2), self.size // 2, 3)
            pygame.draw.circle(self.image, (255, 255, 0), (self.size // 2, self.size // 2), self.size // 3, 2)
        
        self.rect = self.image.get_rect(center=(x, y))

    def set_target(self, player, magnetism_aura_radius=1.0):
        self.target = player
        effective_radius = self.collection_radius * player.level * magnetism_aura_radius
        distance = self.pos.distance_to(player.pos)
        if distance < effective_radius:
            self.is_magnetized = True

    def update(self):
        if self.target and self.is_magnetized:
            direction = self.target.pos - self.pos
            if direction.length_squared() > 0:
                direction = direction.normalize()
                self.pos += direction * self.speed
                self.rect.center = (int(self.pos.x), int(self.pos.y))
                
                if self.pos.distance_to(self.target.pos) < TILE_SIZE / 2:
                    self.target.add_experience(self.amount)
                    self.kill()
        
        # Lógica para evitar que el orbe se vaya al infinito si se pierde el target
        if self.target:
             # Usa SCREEN_WIDTH y SCREEN_HEIGHT
            if self.pos.y > self.target.pos.y + SCREEN_HEIGHT * 2 or \
               self.pos.y < self.target.pos.y - SCREEN_HEIGHT * 2 or \
               self.pos.x > self.target.pos.x + SCREEN_WIDTH * 2 or \
               self.pos.x < self.target.pos.x - SCREEN_WIDTH * 2:
               self.kill() # Eliminar orbes que estén muy lejos