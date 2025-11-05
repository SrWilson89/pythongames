# player.py

import pygame
import math 
from projectile import Projectile
from config import TILE_SIZE, PLAYER_START_SPEED, EXPERIENCE_PER_LEVEL
from abilities import HABILIDADES_MAESTRAS

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        
        # 1. Configuración Visual (Pixel Art)
        try:
            self.image = pygame.image.load("assets/sprites/player.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((0, 255, 0))
            
        self.rect = self.image.get_rect(center=(x, y))

        # 2. Estadísticas
        self.speed = PLAYER_START_SPEED
        self.health = 100
        self.max_health = 100
        
        # 3. Progresión
        self.level = 1
        self.exp = 0
        self.next_level_exp = EXPERIENCE_PER_LEVEL
        
        # 4. Habilidades y Skips
        self.active_abilities = {} 
        self.skips_restantes = 3 
        
        # 5. Cooldowns y AoE
        self.last_daga_fire = 0 # Cooldown para proyectiles (Daga/Bumerán)
        self.aura_fuego_active = None 

    def update(self, keys):
        """Maneja el movimiento y chequea ataques."""
        
        dx, dy = 0, 0
        if keys[pygame.K_w]: dy -= self.speed
        if keys[pygame.K_s]: dy += self.speed
        if keys[pygame.K_a]: dx -= self.speed
        if keys[pygame.K_d]: dx += self.speed

        if dx != 0 and dy != 0:
            factor = self.speed / (2**0.5)
            dx = factor if dx > 0 else -factor
            dy = factor if dy > 0 else -factor
            
        self.rect.x += dx
        self.rect.y += dy

        return self._check_attacks() 

    def _check_attacks(self):
        """Dispara automáticamente las habilidades activas (si están listas)."""
        current_time = pygame.time.get_ticks()
        attack_data = None
        
        # Comprobar Daga Rápida (ID 1)
        if 1 in self.active_abilities:
            nivel_actual = self.active_abilities[1]
            try:
                params = HABILIDADES_MAESTRAS[1]["niveles"][nivel_actual - 1]
            except IndexError:
                params = None
                
            if params and current_time - self.last_daga_fire > params["cooldown"]:
                self.last_daga_fire = current_time
                attack_data = {"type": "Projectile", "damage": params["damage"], "count": params["count"]}
        
        # Comprobar Aura de Fuego (ID 3)
        if 3 in self.active_abilities:
            nivel_actual = self.active_abilities[3]
            params = HABILIDADES_MAESTRAS[3]["niveles"][nivel_actual - 1]
            
            if self.aura_fuego_active is None:
                return {"type": "AuraFuego", "params": params}
            
            else:
                self.aura_fuego_active.damage = params["damage"]
                self.aura_fuego_active.radius = params["radius"]
                self.aura_fuego_active.cooldown = params["cooldown"]
                
        # Comprobar Bumerán Gigante (ID 4)
        if 4 in self.active_abilities:
            nivel_actual = self.active_abilities[4]
            params = HABILIDADES_MAESTRAS[4]["niveles"][nivel_actual - 1]
            
            # Usamos last_daga_fire como un cooldown general para proyectiles
            if current_time - self.last_daga_fire > params["cooldown"]:
                self.last_daga_fire = current_time
                return {"type": "Bumerang", "params": params}

        return attack_data 

    def gain_exp(self, amount):
        """Añade experiencia y comprueba si sube de nivel."""
        self.exp += amount
        if self.exp >= self.next_level_exp:
            return self.level_up()

    def level_up(self):
        """Procesa la subida de nivel."""
        self.level += 1
        self.exp -= self.next_level_exp
        self.next_level_exp = int(self.next_level_exp * 1.15) 
        return True