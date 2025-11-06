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
            # Asegúrate de que tienes un archivo 'assets/sprites/player.png'
            original_image = pygame.image.load("assets/sprites/player.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill((0, 255, 0)) # Fallback verde
            
        self.rect = self.image.get_rect(center=(x, y))
        
        # 2. Estadísticas
        self.speed = PLAYER_START_SPEED
        self.health = 100
        self.max_health = 100
        self.experience = 0
        self.level = 1
        
        # 3. Habilidades y Skips
        # Inicialización con habilidades base para testing
        self.active_abilities = {
            1: 1,  # Daga Rápida Nivel 1
            4: 1,  # Bumerán Gigante Nivel 1
            3: 1,  # Aura de Fuego Nivel 1
        }
        self.skips_restantes = 3 
        
        # 4. Cooldowns
        self.last_daga_fire = 0 
        self.last_bumerang_fire = 0
        self.aura_fuego_active = None 
        
        # --- Posición del Ratón ---
        self.mouse_pos = (x, y) 
        
    def update_mouse_pos(self, pos):
        """Actualiza la posición del ratón."""
        self.mouse_pos = pos

    def move(self, keys):
        """Maneja el movimiento en base a las teclas WASD o flechas."""
        dx, dy = 0, 0
        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed
            
        # Normalizar el movimiento diagonal
        if dx != 0 and dy != 0:
            factor = self.speed / math.sqrt(dx*dx + dy*dy)
            dx *= factor
            dy *= factor

        self.rect.x += int(dx)
        self.rect.y += int(dy)

    def update(self, keys):
        """
        Maneja el movimiento y chequea ataques. 
        Llamado directamente desde main.py con el argumento 'keys'.
        """
        self.move(keys)
        return self._check_attacks() 

    def _check_attacks(self):
        """Dispara automáticamente las habilidades activas (si están listas)."""
        current_time = pygame.time.get_ticks()
        attack_data = None
        
        # 1. Comprobar Daga Rápida (ID 1)
        if 1 in self.active_abilities:
            nivel_actual = self.active_abilities[1]
            try:
                params = HABILIDADES_MAESTRAS[1]["niveles"][nivel_actual - 1]
            except IndexError:
                params = None
                
            if params and current_time - self.last_daga_fire > params["cooldown"]:
                self.last_daga_fire = current_time
                
                # Calcular el vector de dirección hacia la última posición conocida del ratón
                player_center = pygame.math.Vector2(self.rect.center)
                target_pos = pygame.math.Vector2(self.mouse_pos)
                
                direction_vector = target_pos - player_center
                if direction_vector.length_squared() > 0:
                    direction_vector = direction_vector.normalize()
                else:
                    direction_vector = pygame.math.Vector2(1, 0) 
                
                # Crear direcciones con spread (dispersión)
                spread_directions = []
                for i in range(params["count"]):
                    angle = math.atan2(direction_vector.y, direction_vector.x)
                    if params["count"] > 1:
                        # Si hay múltiples dagas, añadir un pequeño ángulo de dispersión
                        deviation = math.radians(random.uniform(-5, 5)) 
                        angle += deviation
                        
                    final_direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    spread_directions.append(final_direction)

                attack_data = {
                    "type": "Projectile", 
                    "damage": params["damage"], 
                    "directions": spread_directions
                }
        
        # 2. Comprobar Bumerán Gigante (ID 4)
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
        
        # 3. Comprobar Aura de Fuego (ID 3)
        if 3 in self.active_abilities:
            nivel_actual = self.active_abilities[3]
            params = HABILIDADES_MAESTRAS[3]["niveles"][nivel_actual - 1]
            
            if not self.aura_fuego_active or current_time - self.aura_fuego_active > params["cooldown"]:
                 self.aura_fuego_active = current_time
                 attack_data = {
                     "type": "AuraFuego",
                     "damage": params["damage"],
                     "radius": params["radius"],
                     "cooldown": params["cooldown"],
                 }
            
        return attack_data
    
    # --- LÓGICA DE NIVEL ---

    def apply_ability_choice(self, choice: tuple):
        """
        Aplica la habilidad elegida (subida de nivel o nueva habilidad)
        al diccionario self.active_abilities.
        :param choice: Tupla (id_habilidad, tipo_mejora)
        """
        hid, tipo = choice
        
        if tipo == "Nueva":
            # Si es nueva, se inicia en nivel 1
            self.active_abilities[hid] = 1
        elif tipo == "Mejora":
            # Si es mejora, se incrementa el nivel actual
            if hid in self.active_abilities:
                current_level = self.active_abilities[hid]
                max_level = HABILIDADES_MAESTRAS[hid]["max_nivel"]
                
                if current_level < max_level:
                    self.active_abilities[hid] += 1
        
        # Reiniciar la experiencia para el siguiente nivel, si la transición fue exitosa
        # (Aunque el chequeo principal se hace en main.py)
        # self.experience = 0 # O ajustar la experiencia restante si se implementa
        
    def add_experience(self, amount):
        """Añade experiencia y comprueba si hay subida de nivel."""
        self.experience += amount
        
        # Si la experiencia excede el requisito, sube de nivel
        if self.experience >= self.level * EXPERIENCE_PER_LEVEL:
            # Consume la experiencia necesaria para el nivel y avanza
            self.experience -= self.level * EXPERIENCE_PER_LEVEL
            self.level += 1
            return True # Señaliza que el menú de nivel debe aparecer
        return False