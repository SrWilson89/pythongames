# bomb.py
import pygame
import random
import os 
import sys 
from config import TILE_SIZE

# FIX: Importar la clase Enemy para la verificación de tipo
from enemies import Enemy 

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

class Bomb(pygame.sprite.Sprite):
    def __init__(self, x, y, damage, radius_multiplier, fall_time, groups, orbs_group):
        super().__init__(groups)
        
        self.damage = damage
        self.fall_time = fall_time
        self.radius_multiplier = radius_multiplier
        self.orbs_group = orbs_group
        
        self.timer = 0
        self.exploded = False
        # El grupo de enemigos se pasa aquí
        self.target_enemies = groups # El grupo de enemigos está en el grupo principal
        
        # Posición y Radio
        self.pos = pygame.math.Vector2(x, y)
        self.base_radius = TILE_SIZE * 1.5
        self.explosion_radius = int(self.base_radius * self.radius_multiplier)
        self.current_radius = TILE_SIZE // 4
        
        try:
            grenade_path = resource_path("assets/sprites/granade.png")
            original = pygame.image.load(grenade_path).convert_alpha()
            size = (TILE_SIZE // 2, TILE_SIZE // 2)
            self.original_image = pygame.transform.scale(original, size)
            self.image = self.original_image.copy()
        except pygame.error as e:
            print(f"ERROR granade.png: {e}")
            self.image = pygame.Surface((TILE_SIZE // 2, TILE_SIZE // 2), pygame.SRCALPHA)
            pygame.draw.circle(self.image, (150, 150, 150), (TILE_SIZE // 4, TILE_SIZE // 4), TILE_SIZE // 4)
            self.original_image = self.image.copy()
            
        self.rect = self.image.get_rect(center=(x, y))
        
    def update(self):
        if not self.exploded:
            # Animación de caída (hacer crecer la bomba)
            fall_progress = min(1.0, self.timer / self.fall_time)
            target_radius = TILE_SIZE // 4 + (self.base_radius - TILE_SIZE // 4) * fall_progress
            self.current_radius = int(target_radius)
            
            # Escalar la imagen (sólo para la caída)
            size = (self.current_radius * 2, self.current_radius * 2)
            self.image = pygame.transform.scale(self.original_image, size)
            self.rect = self.image.get_rect(center=self.pos)
            
            self.timer += 1
        else:
            # Después de la explosión, animar el flash y luego matar
            self.timer += 1
            if self.timer > 10: # Duración del flash
                self.kill()


        if self.timer >= self.fall_time and not self.exploded:
            self.exploded = True
            
            # === APLICAR DAÑO ===
            hit_enemies = []
            for sprite in self.target_enemies:
                # Comprueba si es un enemigo (clase Enemy) y si está dentro del radio de la explosión
                if (isinstance(sprite, Enemy) and  # <--- CORREGIDO
                        sprite.name != 'Bomb' and  # Excluir bombas
                        self.pos.distance_to(sprite.pos) < self.explosion_radius):
                        hit_enemies.append(sprite)

            # === GENERAR ORBES ===
            from experience_orb import ExperienceOrb 
            for enemy in hit_enemies:
                if enemy.take_damage(self.damage):
                    # El valor 1 es la cantidad de experiencia base
                    ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (self.orbs_group,))

            # === EXPLOSIÓN VISUAL (PREPARACIÓN) ===
            self.timer = 0 # Reiniciar timer para la animación de flash
            
            # Crear una superficie de explosión (se dibuja en draw_custom)
            self.image = pygame.Surface((self.explosion_radius * 3, self.explosion_radius * 3), pygame.SRCALPHA)
            self.rect = self.image.get_rect(center=self.pos)
            # Asegurarse de que el objeto no sea considerado para colisión de enemigos después de explotar
            self.target_enemies.remove(self)
            

    def draw_custom(self, surface, offset):
        # Aplicar el offset a la posición de dibujo
        draw_center_x = self.pos.x - offset.x
        draw_center_y = self.pos.y - offset.y
        draw_rect = self.rect.copy()
        draw_rect.center = (int(draw_center_x), int(draw_center_y))

        if not self.exploded:
            # Dibuja la sombra
            shadow_radius = self.current_radius * 0.6
            
            # Posición de la sombra APLICANDO EL OFFSET
            shadow_center_x = int(draw_center_x)
            shadow_center_y = int(draw_rect.bottom - 5)
            
            pygame.draw.circle(surface, (0, 0, 0, 80), 
                             (shadow_center_x, shadow_center_y), 
                             int(shadow_radius))
            
            # Dibuja la bomba APLICANDO EL OFFSET
            surface.blit(self.image, draw_rect)
        else:
            # Animación de flash de la explosión
            alpha = max(0, 255 - int(255 * (self.timer / 10)))
            color = (255, 180, 0, alpha)
            
            # Dibujar un círculo blanco/amarillo pulsante
            radius = self.explosion_radius * (1 + self.timer / 10) # Hace que crezca ligeramente
            
            temp = pygame.Surface((radius * 2, radius * 2), pygame.SRCALPHA)
            pygame.draw.circle(temp, color, (radius, radius), radius)
            
            # Aplicar el offset a la posición del círculo de explosión
            temp_rect = temp.get_rect(center=(draw_center_x, draw_center_y))
            surface.blit(temp, temp_rect)