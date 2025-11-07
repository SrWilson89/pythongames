# player.py
import pygame
import math
import random
from config import TILE_SIZE, PLAYER_START_SPEED, EXPERIENCE_PER_LEVEL
from abilities import HABILIDADES_MAESTRAS

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # 1. Configuración Visual
        try:
            original_image = pygame.image.load("assets/sprites/player.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Estadísticas
        self.speed = PLAYER_START_SPEED
        self.health = 100
        self.max_health = 100
        self.experience = 0
        self.level = 1
        
        # 3. Habilidades y Timers (Cooldowns se miden en milisegundos de Pygame)
        self.active_abilities = {
            1: 1,  # Daga Rápida Nivel 1
            4: 1,  # Bumerán Gigante Nivel 1
            3: 1,  # Aura de Fuego Nivel 1
            2: 1,  # Rayo de Escarcha Nivel 1
            5: 1,  # Aura de Magnetismo Nivel 1
        }
        
        # Timers de Cooldown (Inicializados a 0)
        self.last_dagger_fire = 0
        self.last_ray_fire = 0
        self.last_bumerang_fire = 0
        self.last_fire_aura_tick = 0
        self.last_magnet_aura_update = 0
        
        # Posición vectorial para movimiento suave
        self.pos = pygame.math.Vector2(self.rect.center)
        
    def update(self):
        """Maneja la entrada del teclado y actualiza la posición."""
        
        # 1. Manejo de Input
        keys = pygame.key.get_pressed()
        
        # Obtener la dirección del movimiento
        direction = pygame.math.Vector2(0, 0)
        if keys[pygame.K_w]:
            direction.y = -1
        if keys[pygame.K_s]:
            direction.y = 1
        if keys[pygame.K_a]:
            direction.x = -1
        if keys[pygame.K_d]:
            direction.x = 1
            
        # 2. Movimiento
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
            
        # Actualizar el rect
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
    def get_attack_data(self):
        """Comprueba si alguna habilidad debe activarse basado en el cooldown."""
        
        attack_data = None
        current_time = pygame.time.get_ticks()
        
        # --- Habilidad 1: Daga Rápida ---
        if 1 in self.active_abilities:
            nivel_actual = self.active_abilities[1]
            try:
                params = HABILIDADES_MAESTRAS[1]["niveles"][nivel_actual - 1]
            except IndexError:
                params = None 

            if params and current_time - self.last_dagger_fire > params["cooldown"]:
                self.last_dagger_fire = current_time
                attack_data = {
                    "type": "Daga Rápida",
                    "damage": params["damage"],
                    "count": params["count"],
                }
                
        # --- Habilidad 2: Rayo de Escarcha ---
        if 2 in self.active_abilities:
            nivel_actual = self.active_abilities[2]
            try:
                params = HABILIDADES_MAESTRAS[2]["niveles"][nivel_actual - 1]
            except IndexError:
                params = None

            if params and current_time - self.last_ray_fire > params["cooldown"]:
                self.last_ray_fire = current_time
                attack_data = {
                    "type": "Rayo de Escarcha",
                    "damage": params["damage"],
                    "speed": params["speed"],
                }
                
        # --- Habilidad 3: Aura de Fuego ---
        if 3 in self.active_abilities:
            nivel_actual = self.active_abilities[3]
            try:
                params = HABILIDADES_MAESTRAS[3]["niveles"][nivel_actual - 1]
            except IndexError:
                params = None

            # Esto se dispara UNA SOLA VEZ para crear o actualizar el aura en main.py
            if params and current_time - self.last_fire_aura_tick > 100: # Cooldown corto para asegurar la existencia
                self.last_fire_aura_tick = current_time
                attack_data = {
                    "type": "Aura de Fuego",
                    "damage": params["damage"],
                    "cooldown": params["cooldown"],
                    "radius": params["radius"], 
                }
                
        # --- Habilidad 5: Aura de Magnetismo ---
        if 5 in self.active_abilities:
            nivel_actual = self.active_abilities[5]
            try:
                params = HABILIDADES_MAESTRAS[5]["niveles"][nivel_actual - 1]
            except IndexError:
                params = None

            if params and current_time - self.last_magnet_aura_update > 100: 
                self.last_magnet_aura_update = current_time
                attack_data = {
                    "type": "Aura de Magnetismo",
                    "damage": params["damage"], 
                    "cooldown": params["cooldown"], 
                    "radius": params["radius"], # Multiplicador de radio de recolección
                }
                
        # --- Habilidad 4: Bumerán ---
        if 4 in self.active_abilities:
            nivel_actual = self.active_abilities[4]
            try:
                params = HABILIDADES_MAESTRAS[4]["niveles"][nivel_actual - 1]
            except IndexError:
                params = None
                
            if params and current_time - self.last_bumerang_fire > params["cooldown"]:
                self.last_bumerang_fire = current_time
                attack_data = {
                    "type": "Bumerang",
                    "damage": params["damage"],
                    "speed": params["speed"],
                    "lifetime": params["lifetime"],
                    "count": params["count"], 
                }
        
        return attack_data
    
    def apply_ability_choice(self, choice: tuple):
        hid, tipo = choice
        
        if tipo == "Nueva":
            self.active_abilities[hid] = 1
        elif tipo == "Mejora":
            if hid in self.active_abilities:
                current_level = self.active_abilities[hid]
                max_level = HABILIDADES_MAESTRAS[hid]["max_nivel"]
                
                if current_level < max_level:
                    self.active_abilities[hid] += 1
        
    def add_experience(self, amount):
        self.experience += amount
        
        # Experiencia Requerida = Nivel Actual * EXPERIENCE_PER_LEVEL
        if self.experience >= self.level * EXPERIENCE_PER_LEVEL:
            self.experience -= self.level * EXPERIENCE_PER_LEVEL
            self.level += 1
            return True 
        return False