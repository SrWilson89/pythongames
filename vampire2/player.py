# player.py
import pygame
import math
import random
import sys
import os # <-- AÑADIDO
from config import TILE_SIZE, PLAYER_START_SPEED, EXPERIENCE_PER_LEVEL
from abilities import HABILIDADES_MAESTRAS
from bomb import Bomb # <-- NECESARIO
from bumerang import Bumerang # <-- NECESARIO
from ray_of_frost import RayOfFrost # <-- NECESARIO
from projectile import Projectile # <-- NECESARIO
from area_ability import AreaAbility # <-- NECESARIO

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA (Añadida para PyInstaller)
# =======================================================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# =======================================================

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Posición
        self.pos = pygame.math.Vector2(x, y) # <-- USAR VECTOR PARA POSICIÓN EXACTA
        
        # Visual
        try:
            # CORRECCIÓN: Usar resource_path
            original_image = pygame.image.load(resource_path("assets/sprites/player.png")).convert_alpha() 
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            # Fallback
            print(f"Advertencia: No se pudo cargar player.png. Usando cuadrado verde. Error: {e}")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect(center=(x, y))
        
        # Stats
        self.speed = PLAYER_START_SPEED
        self.health = 100
        self.max_health = 100
        self.experience = 0
        self.level = 1
        
        # Habilidades
        self.active_abilities = {
            1: 1,  # Daga Rápida
            4: 1,  # Bumerán
            5: 1,  # Bomba Aleatoria
            3: 1,  # Aura de Fuego (Si no lo tenías activado, lo añadimos)
        }
        
        # Grupos (se deben establecer después de la inicialización en main.py)
        self.projectile_group = None
        self.orbs_group = None
        self.enemies_group = None
        self.bumerang_group = None
        self.bomb_group = None
        self.area_group = None
        self.aura_created = False
        
        # Timer de ataque/cooldowns
        self.last_attack_time = {hid: 0 for hid in HABILIDADES_MAESTRAS.keys()}

    def set_groups(self, proj, orbs, enemies, bumerangs, bombs): # Corregida la firma si no usas todos
        self.projectile_group = proj
        self.orbs_group = orbs
        self.enemies_group = enemies
        self.bumerang_group = bumerangs
        self.bomb_group = bombs

    def set_area_group(self, area_group):
        self.area_group = area_group
        
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            print("GAME OVER")
            # Implementar lógica de Game Over aquí
            
    def update(self):
        # 1. Movimiento del jugador
        keys = pygame.key.get_pressed()
        vel_x, vel_y = 0, 0
        if keys[pygame.K_a]: vel_x = -1
        if keys[pygame.K_d]: vel_x = 1
        if keys[pygame.K_w]: vel_y = -1
        if keys[pygame.K_s]: vel_y = 1
        
        movement = pygame.math.Vector2(vel_x, vel_y)
        if movement.length_squared() > 0:
            movement = movement.normalize() * self.speed
            
        self.pos += movement
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
        # 2. Lógica de Ataque
        self.handle_abilities()

    def find_nearest_enemy_direction(self):
        if not self.enemies_group or not self.enemies_group.sprites():
            # Si no hay enemigos, dispara al azar
            return pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        
        # Buscar el enemigo más cercano
        min_distance_sq = float('inf')
        nearest_enemy = None
        player_pos = self.pos
        
        for enemy in self.enemies_group:
            enemy_pos = pygame.math.Vector2(enemy.rect.center)
            distance_sq = (enemy_pos - player_pos).length_squared()
            
            if distance_sq < min_distance_sq:
                min_distance_sq = distance_sq
                nearest_enemy = enemy
        
        if nearest_enemy:
            # Calcular la dirección hacia el enemigo más cercano
            direction = pygame.math.Vector2(nearest_enemy.rect.center) - player_pos
            return direction.normalize()
        
        return pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()

    def handle_abilities(self):
        current_time = pygame.time.get_ticks()

        # Daga Rápida (1)
        if 1 in self.active_abilities:
            lvl = self.active_abilities[1]
            params = HABILIDADES_MAESTRAS[1]["niveles"][lvl - 1]
            
            if current_time - self.last_attack_time[1] >= params["cooldown"]:
                self.last_attack_time[1] = current_time
                for _ in range(params["count"]):
                    # Dirección aleatoria
                    rand_dir = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
                    Projectile(self.rect.centerx, self.rect.centery, rand_dir, params["damage"], (self.projectile_group,), lifetime=120)

        # Rayo de Escarcha (2) - Lo desactivamos para simplificar, pero si está activo...
        if 2 in self.active_abilities:
            lvl = self.active_abilities[2]
            params = HABILIDADES_MAESTRAS[2]["niveles"][lvl - 1]
            
            if current_time - self.last_attack_time[2] >= params["cooldown"]:
                self.last_attack_time[2] = current_time
                for _ in range(params["count"]):
                    # Dirección hacia el enemigo más cercano
                    target_dir = self.find_nearest_enemy_direction()
                    RayOfFrost(self.rect.centerx, self.rect.centery, target_dir, params["damage"], (self.projectile_group,), lifetime=params["lifetime"])

        # Aura de Fuego (3) - Se gestiona en set_area_group
        if 3 in self.active_abilities and not self.aura_created:
             self.aura_created = True
             lvl = self.active_abilities[3]
             params = HABILIDADES_MAESTRAS[3]["niveles"][lvl - 1]
             # Crear la habilidad de área solo una vez
             AreaAbility(self, params["damage"], params["radius"], params["cooldown"], (self.area_group,), ability_type="fire")
        
        # Bumerán (4)
        if 4 in self.active_abilities:
            lvl = self.active_abilities[4]
            params = HABILIDADES_MAESTRAS[4]["niveles"][lvl - 1]
            
            if current_time - self.last_attack_time[4] >= params["cooldown"]:
                self.last_attack_time[4] = current_time
                for _ in range(params["count"]):
                    Bumerang(self, params["damage"], params["speed"], params["lifetime"], (self.bumerang_group,))
                    
        # Bomba Aleatoria (5)
        if 5 in self.active_abilities and self.enemies_group:
            lvl = self.active_abilities[5]
            params = HABILIDADES_MAESTRAS[5]["niveles"][lvl - 1]
            
            if current_time - self.last_attack_time[5] >= params["cooldown"]:
                self.last_attack_time[5] = current_time
                for _ in range(params["count"]):
                    if self.enemies_group.sprites():
                        # Lanza la bomba a un punto aleatorio cerca de un enemigo
                        rand_enemy = random.choice(self.enemies_group.sprites())
                        rand_pos = rand_enemy.pos + pygame.math.Vector2(random.randint(-100, 100), random.randint(-100, 100))
                        
                        Bomb(rand_pos.x, rand_pos.y, params["damage"], params["radius"], params["fall_time"], (self.bomb_group, self.enemies_group), self.orbs_group)

    def should_level_up(self):
        return self.experience >= self.level * EXPERIENCE_PER_LEVEL

    def level_up(self):
        self.level += 1
        self.experience = 0 # Reiniciar la experiencia al subir de nivel

    def add_experience(self, amount):
        self.experience += amount

    def update_fire_aura(self):
         # Lógica para actualizar el Aura de Fuego cuando sube de nivel
         if 3 in self.active_abilities and self.area_group:
             lvl = self.active_abilities[3]
             params = HABILIDADES_MAESTRAS[3]["niveles"][lvl - 1]
             # Busca la instancia de AreaAbility y actualiza sus stats
             for ability in self.area_group.sprites():
                 if isinstance(ability, AreaAbility):
                     ability.damage = params["damage"]
                     ability.radius_multiplier = params["radius"]
                     ability.base_radius = int(TILE_SIZE * 3 * params["radius"])
                     ability.damage_radius = ability.base_radius
                     ability.cooldown = params["cooldown"]
                     # Forzar la recarga del sprite para que refleje el nuevo radio
                     try:
                         original = pygame.image.load(resource_path("assets/sprites/fire_ring.png")).convert_alpha()
                         ability.original_image = pygame.transform.scale(original, (ability.base_radius * 2, ability.base_radius * 2))
                     except pygame.error:
                         pass # Fallback ya está en el __init__