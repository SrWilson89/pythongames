# experience_orb.py
import pygame
import math
from config import TILE_SIZE, GREEN, WHITE

class ExperienceOrb(pygame.sprite.Sprite):
    def __init__(self, x, y, amount, groups):
        super().__init__(groups)
        
        self.amount = amount
        self.size = TILE_SIZE // 2 # Un tamaño pequeño y proporcional
        
        # 1. Configuración Visual (Carga del PNG)
        try:
            # Intentamos cargar la imagen 'experience_orb.png'
            original_image = pygame.image.load("assets/sprites/experience_orb.png").convert_alpha()
            self.image = pygame.transform.scale(original_image, (self.size, self.size))
        except pygame.error:
            # Fallback si la imagen no se encuentra (Círculo Verde)
            self.image = pygame.Surface((self.size, self.size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, GREEN, (self.size // 2, self.size // 2), self.size // 2)
            
        self.rect = self.image.get_rect(center=(x, y))
        self.pos = pygame.math.Vector2(self.rect.center)
        
        # 2. Lógica de Recolección
        self.target = None # Se establecerá al jugador cuando esté cerca
        self.speed = 0 
        self.collection_radius = TILE_SIZE * 3 # Distancia base
        self.is_magnetized = False

    def set_target(self, player, magnetism_aura_radius=1.0):
        """Define al jugador como el objetivo si está dentro del radio."""
        
        # Colección base se multiplica por el factor de magnetismo
        effective_radius = self.collection_radius * magnetism_aura_radius 

        distance = self.pos.distance_to(player.pos)
        if distance < effective_radius: 
            self.target = player
            
    def update(self):
        """Mueve el orbe hacia el jugador si está activo."""
        
        if self.target:
            # Cálculo de dirección
            target_pos = pygame.math.Vector2(self.target.rect.center)
            direction_vector = target_pos - self.pos
            
            if direction_vector.length_squared() > 0:
                direction_vector = direction_vector.normalize()
            
            # Acelerar gradualmente la velocidad
            self.speed = min(self.speed + 0.15, 8) 
            
            # Mover
            self.pos += direction_vector * self.speed
            self.rect.center = (int(self.pos.x), int(self.pos.y))