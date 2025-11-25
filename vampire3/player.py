# player.py
import pygame
import math
import random
import sys
from config import TILE_SIZE, PLAYER_START_SPEED, EXPERIENCE_PER_LEVEL
from abilities import HABILIDADES_MAESTRAS

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # Visual
        try:
            original_image = pygame.image.load("assets/sprites/player.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
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
            2: 1,  # Rayo de Escarcha
            3: 1,  # Aura de Fuego
            4: 1,  # Bumerán
            5: 1,  # Bomba Aleatoria
        }
        
        # Timers
        self.last_fire_time = 0
        self.last_frost_time = 0
        self.last_bumerang_time = 0
        self.last_bomb_time = 0
        self.aura_created = False

        self.pos = pygame.math.Vector2(self.rect.center)
        
        # ¡NUEVO: Referencia al grupo de auras!
        self.area_abilities_group = None

    def set_area_group(self, group):
        """Se llama desde main.py después de crear el grupo"""
        self.area_abilities_group = group

    def update(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]: dy -= 1
        if keys[pygame.K_s] or keys[pygame.K_DOWN]: dy += 1
        if keys[pygame.K_a] or keys[pygame.K_LEFT]: dx -= 1
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]: dx += 1
            
        direction = pygame.math.Vector2(dx, dy)
        if direction.length_squared() > 0:
            direction = direction.normalize()
            self.pos += direction * self.speed
        self.rect.center = (int(self.pos.x), int(self.pos.y))

    def take_damage(self, amount):
        self.health = max(0, self.health - amount)
        print(f"DAÑO: {amount}HP | HP: {self.health}/{self.max_health}")
        if self.health <= 0:
            print("GAME OVER")
            pygame.quit()
            sys.exit()

    def level_up_health(self):
        self.max_health = min(200, self.max_health + 10)
        self.health = min(self.max_health, self.health + 10)
        print(f"REGENERADO: +10HP | Máx: {self.max_health}")

    def update_fire_aura(self):
        """ACTUALIZA AURA SIN DEPENDER DE all_sprites"""
        if not self.area_abilities_group:
            return  # Aún no asignado
        
        nivel = self.active_abilities.get(3, 0)
        if nivel == 0:
            return
        
        params = HABILIDADES_MAESTRAS[3]["niveles"][nivel - 1]
        damage = params["damage"]
        radius_multiplier = params["radius"]
        cooldown = params["cooldown"]
        
        # Buscar en el grupo de auras
        for ability in self.area_abilities_group:
            if ability.ability_type == "fire":
                ability.damage = damage
                ability.damage_radius = int(TILE_SIZE * 3 * radius_multiplier)
                ability.cooldown = cooldown
                print(f"AURA ACTUALIZADA: Radio x{radius_multiplier} | Daño {damage}")
                break

    def get_attack_data(self):
        current_time = pygame.time.get_ticks()
        attacks = []

        if 1 in self.active_abilities:
            nivel = self.active_abilities[1]
            params = HABILIDADES_MAESTRAS[1]["niveles"][nivel - 1]
            if current_time - self.last_fire_time >= params["cooldown"]:
                attacks.append({
                    "type": "Daga Rápida",
                    "damage": params["damage"],
                    "count": params["count"]
                })

        if 2 in self.active_abilities:
            nivel = self.active_abilities[2]
            params = HABILIDADES_MAESTRAS[2]["niveles"][nivel - 1]
            if current_time - self.last_frost_time >= params["cooldown"]:
                attacks.append({
                    "type": "Rayo de Escarcha",
                    "damage": params["damage"],
                    "speed": params["speed"]
                })

        if 4 in self.active_abilities:
            nivel = self.active_abilities[4]
            params = HABILIDADES_MAESTRAS[4]["niveles"][nivel - 1]
            if current_time - self.last_bumerang_time >= params["cooldown"]:
                attacks.append({
                    "type": "Bumerang",
                    "damage": params["damage"],
                    "speed": params["speed"],
                    "lifetime": params["lifetime"],
                    "count": params["count"]
                })

        if 5 in self.active_abilities:
            nivel = self.active_abilities[5]
            params = HABILIDADES_MAESTRAS[5]["niveles"][nivel - 1]
            if current_time - self.last_bomb_time >= params["cooldown"]:
                attacks.append({
                    "type": "Bomba Aleatoria",
                    "damage": params["damage"],
                    "radius": params["radius"],
                    "count": params["count"],
                    "fall_time": params["fall_time"]
                })

        if 3 in self.active_abilities and not self.aura_created:
            self.aura_created = True
            nivel = self.active_abilities[3]
            params = HABILIDADES_MAESTRAS[3]["niveles"][nivel - 1]
            attacks.append({
                "type": "Aura de Fuego",
                "damage": params["damage"],
                "radius": params["radius"],
                "cooldown": params["cooldown"]
            })

        return attacks

    def add_new_ability(self, hid: int):
        self.active_abilities[hid] = 1
        print(f"NUEVA HABILIDAD: {hid}")

    def upgrade_ability(self, hid: int):
        if hid in self.active_abilities:
            current = self.active_abilities[hid]
            max_lvl = HABILIDADES_MAESTRAS[hid]["max_nivel"]
            if current < max_lvl:
                self.active_abilities[hid] += 1
                print(f"MEJORADA: {hid} -> Nv.{self.active_abilities[hid]}")
                if hid == 3:
                    self.update_fire_aura()

    def add_experience(self, amount):
        self.experience += amount
        if self.experience >= self.level * EXPERIENCE_PER_LEVEL:
            self.experience -= self.level * EXPERIENCE_PER_LEVEL
            self.level += 1
            self.level_up_health()
            print(f"¡NIVEL {self.level}!")
            return True
        return False