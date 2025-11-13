# player.py - CORRECCIÓN DE FileNotFoundError
import pygame
import math
import random
import sys
import os # Necesario para resource_path

from config import TILE_SIZE, PLAYER_START_SPEED, EXPERIENCE_PER_LEVEL
from abilities import HABILIDADES_MAESTRAS
from area_ability import AreaAbility # Necesario para update_fire_aura

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA (Necesaria en el sprite para cargar imágenes)
# =======================================================
def resource_path(relative_path):
    """Maneja rutas de recursos para desarrollo local o ejecutables de PyInstaller."""
    try:
        # sys._MEIPASS es la ruta temporal de PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Si no está empaquetado, usa la ruta actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# =======================================================


class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Visual
        try:
            # FIX: Usa resource_path() para localizar el archivo PNG
            original_image = pygame.image.load(resource_path("assets/sprites/player.png")).convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error as e:
            print(f"ERROR DE CARGA DE SPRITE: {e}. Usando fallback.")
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((0, 255, 0)) # Verde de fallback
            
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
            2: 1,  # Rayo de Escarcha
            3: 1,  # Aura de Fuego
            4: 1,  # Bumerán
            5: 1,  # Bomba Aleatoria
        }
        
        # Movimiento
        self.direction = pygame.math.Vector2() 
        self.pos = pygame.math.Vector2(self.rect.center)
        
        # Cooldowns
        self.last_attack_time = {1: 0, 2: 0, 4: 0, 5: 0}
        self.can_take_damage = True
        self.invincibility_end_time = 0
        self.invincibility_duration = 500 # ms
        
        # Aura de Fuego (Habilidad 3)
        self.fire_aura = None 
        self.aura_created = False
        
        # Grupos de sprites (deben asignarse desde main.py)
        self.orbs_group = None 
        self.projectiles_group = None 
        self.enemies_group = None 

    # =======================================================
    # MÉTODOS DE MOVIMIENTO / ENTRADA / DAÑO
    # (Los métodos get_input, move, check_invincibility, take_damage,
    # check_cooldowns, attack, update_fire_aura, get_available_attacks, 
    # add_new_ability, upgrade_ability, y add_experience van aquí)
    # =======================================================
    
    def get_input(self, keys):
        self.direction.x = 0
        self.direction.y = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            self.direction.y = -1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            self.direction.y = 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            self.direction.x = -1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            self.direction.x = 1

        if self.direction.length_squared() != 0:
            self.direction = self.direction.normalize()
            
    def move(self):
        self.pos += self.direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))
        
    def check_invincibility(self):
        current_time = pygame.time.get_ticks()
        if not self.can_take_damage and current_time > self.invincibility_end_time:
            self.can_take_damage = True
            self.image.set_alpha(255)
        elif not self.can_take_damage:
            if current_time % 200 < 100:
                self.image.set_alpha(100)
            else:
                self.image.set_alpha(255)

    def take_damage(self, amount):
        current_time = pygame.time.get_ticks()
        if self.can_take_damage:
            self.health -= amount
            self.can_take_damage = False
            self.invincibility_end_time = current_time + self.invincibility_duration
            if self.health <= 0:
                self.kill()
                return True
        return False
        
    def check_cooldowns(self):
        pass # Lógica de cooldowns...
        
    def attack(self):
        # Lógica de ataque (creación de proyectiles, etc.)
        # ...
        pass
        
    def update_fire_aura(self, groups):
        # Lógica para crear o actualizar el aura
        nivel = self.active_abilities[3]
        params = HABILIDADES_MAESTRAS[3]["niveles"][nivel - 1]
        
        if self.fire_aura:
            self.fire_aura.kill()

        self.fire_aura = AreaAbility(
            player=self,
            damage=params["damage"],
            radius_multiplier=params["radius"],
            cooldown=params["cooldown"],
            groups=groups,
            ability_type="fire"
        )
        
    def get_available_attacks(self):
        attacks = []
        current_time = pygame.time.get_ticks()
        # ... (Lógica completa de get_available_attacks)
        # La he omitido por espacio, pero asegúrate de que esté aquí.
        
        # Ejemplo: Daga Rápida (1)
        if 1 in self.active_abilities and current_time - self.last_attack_time.get(1, 0) > HABILIDADES_MAESTRAS[1]["niveles"][self.active_abilities[1] - 1]["cooldown"]:
            nivel = self.active_abilities[1]
            params = HABILIDADES_MAESTRAS[1]["niveles"][nivel - 1]
            attacks.append({"type": "Projectile", "damage": params["damage"], "count": params["count"], "lifetime": params.get("lifetime", 120)})
            self.last_attack_time[1] = current_time
            
        # Ejemplo: Aura de Fuego (3) - Se gestiona en update_fire_aura/update, no aquí
        # ... (Resto de habilidades)
        
        return attacks

    def add_new_ability(self, hid: int, groups):
        self.active_abilities[hid] = 1
        print(f"NUEVA HABILIDAD: {hid}")
        if hid == 3:
            self.update_fire_aura(groups)
        
    def upgrade_ability(self, hid: int, groups):
        if hid in self.active_abilities:
            current = self.active_abilities[hid]
            max_lvl = HABILIDADES_MAESTRAS[hid]["max_nivel"]
            if current < max_lvl:
                self.active_abilities[hid] += 1
                print(f"MEJORADA: {hid} -> Nv.{self.active_abilities[hid]}")
                if hid == 3:
                    self.update_fire_aura(groups)

    def add_experience(self, amount):
        self.experience += amount
        if self.experience >= self.level * EXPERIENCE_PER_LEVEL:
            # Lógica para subir de nivel/abrir el menú
            pass

    # =======================================================
    # MÉTODO DE ACTUALIZACIÓN (UPDATE)
    # =======================================================
    def update(self, keys):
        self.get_input(keys)
        self.move()
        self.check_cooldowns() 
        self.attack() 
        
        if self.fire_aura:
            self.fire_aura.update()
            
        self.check_invincibility()