# area_ability.py
import pygame
import math
from config import TILE_SIZE, WHITE

class AreaAbility(pygame.sprite.Sprite):
    """
    Clase dedicada a habilidades de área estáticas centradas en el jugador.
    Ahora solo maneja el Aura de Fuego (usando fire_ring.png).
    """
    def __init__(self, player, damage, radius, cooldown, groups, ability_type="fire"): 
        super().__init__(groups)
        self.player = player
        self.damage = damage
        self.cooldown = cooldown
        self.ability_type = ability_type 

        # --- Lógica de Fuego (fire_ring.png) ---
        
        # 'radius' es el multiplicador de tamaño de área de daño.
        self.damage_radius_multiplier = radius 
        
        # Cálculo del tamaño (Asegura un tamaño base mínimo de TILE_SIZE * 2)
        self.target_size = int(self.damage_radius_multiplier * (TILE_SIZE * 2)) 
        if self.target_size < TILE_SIZE * 2: 
            self.target_size = TILE_SIZE * 2
        
        self.damage_radius = self.target_size // 2 

        self.original_image_loaded = None 
        
        # El nombre correcto del PNG solicitado por el usuario es 'fire_ring.png'
        PNG_PATH = "assets/sprites/fire_ring.png" 

        try:
            # Carga la imagen de anillo y la escala
            loaded_image = pygame.image.load(PNG_PATH).convert_alpha() 
            self.original_image_loaded = pygame.transform.scale(loaded_image, (self.target_size, self.target_size))
            self.image = self.original_image_loaded.copy() 
            
        except pygame.error:
            # Fallback (Círculo Rojo Suave) si el PNG no se encuentra
            print("=====================================================================")
            print(f"¡ADVERTENCIA! No se encontró '{PNG_PATH}'.")
            print("Usando fallback circular para Aura de Fuego.")
            print("=====================================================================")
            
            TEST_RED_SOFT = (255, 50, 50, 100) # Rojo semi-transparente
            self.image = pygame.Surface((self.target_size, self.target_size), pygame.SRCALPHA)
            pygame.draw.circle(self.image, TEST_RED_SOFT, (self.damage_radius, self.damage_radius), self.damage_radius)
        
        self.rect = self.image.get_rect(center=self.player.rect.center)
            
        self.last_damage_time = 0
        self.angle = 0 
        
    def update(self):
        """Actualiza la posición y rotación del sprite."""
        
        center_x, center_y = self.player.rect.center
        
        # Solo aplica lógica de rotación/offset si el PNG fue cargado
        if self.original_image_loaded:
            # Lógica de rotación para Fuego
            self.angle = (self.angle + 3) % 360 
            self.image = pygame.transform.rotate(self.original_image_loaded, self.angle)
            
            # Compensación vertical para el efecto visual
            vertical_offset = TILE_SIZE // 4 
            self.rect = self.image.get_rect(center=(center_x, center_y + vertical_offset))
        
        else:
             # Si usa el fallback, solo sigue al jugador (sin offset)
             self.rect.center = (center_x, center_y) 
        
    def draw_custom(self, surface):
        """Dibuja el Aura de Fuego."""
        surface.blit(self.image, self.rect)