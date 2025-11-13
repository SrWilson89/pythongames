# area_ability.py - VERSIÓN CORREGIDA
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

class AreaAbility(pygame.sprite.Sprite):
    def __init__(self, player, damage, radius_multiplier, cooldown, groups, ability_type="fire"):
        super().__init__(groups)
        self.player = player
        self.damage = damage
        self.radius_multiplier = radius_multiplier
        self.cooldown = cooldown
        self.ability_type = ability_type

        # RADIO BASE
        self.base_radius = int(TILE_SIZE * 3 * radius_multiplier)
        self.damage_radius = self.base_radius

        # CARGAR TU PNG PERSONALIZADO
        try:
            # Usa resource_path para la carga
            original = pygame.image.load(resource_path("assets/sprites/fire_ring.png")).convert_alpha()
            self.original_image = pygame.transform.scale(original, (self.base_radius * 2, self.base_radius * 2))
        except pygame.error as e:
            print(f"ERROR: fire_ring.png no encontrado → {e}")
            # Fallback (Círculo semi-transparente)
            self.original_image = pygame.Surface((self.base_radius * 2, self.base_radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.original_image, (255, 100, 0, 100), (self.base_radius, self.base_radius), self.base_radius, 8)

        self.image = self.original_image.copy()
        self.rect = self.image.get_rect(center=player.rect.center)
        self.last_damage_time = 0
        self.rotation = 0  # Para efecto de rotación

    def update(self):
        self.rect.center = self.player.rect.center
        self.rotation = (self.rotation + 1) % 360  # Rotación lenta
        # self.image = pygame.transform.rotate(self.original_image, self.rotation) # Desactivado para evitar la rotación excesiva
        self.rect = self.image.get_rect(center=self.player.rect.center)

    def draw_custom(self, surface, offset): # <--- CORREGIDO: RECIBE Y USA EL OFFSET
        if self.ability_type == "fire":
            # PULSO DE TAMAÑO
            pulse = 0.95 + 0.05 * math.sin(pygame.time.get_ticks() * 0.008)
            current_size = int(self.base_radius * 2 * pulse)
            
            # Escalar imagen con pulso
            scaled = pygame.transform.scale(self.original_image, (current_size, current_size))
            
            # Calcular la posición en pantalla APLICANDO EL OFFSET
            # Se usa el centro del jugador menos el offset de la cámara
            scaled_rect = scaled.get_rect(center=(self.rect.centerx - offset.x, self.rect.centery - offset.y))
            surface.blit(scaled, scaled_rect)
            
    def check_damage(self, enemies_group):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.cooldown:
            self.last_damage_time = current_time
            
            # Colisiones: solo revisa si el centro del enemigo está dentro del radio
            hit_enemies = []
            radius_squared = self.damage_radius**2
            
            for enemy in enemies_group:
                distance_sq = (self.rect.centerx - enemy.rect.centerx)**2 + \
                              (self.rect.centery - enemy.rect.centery)**2
                
                if distance_sq < radius_squared:
                    hit_enemies.append(enemy)
            
            # Aplicar daño
            for enemy in hit_enemies:
                enemy.take_damage(self.damage)