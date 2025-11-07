# area_ability.py
import pygame
import math
from config import TILE_SIZE, WHITE

class AreaAbility(pygame.sprite.Sprite):
    # AÑADE EL PARÁMETRO ability_type
    def __init__(self, player, damage, radius, cooldown, groups, ability_type="fire"): 
        super().__init__(groups)
        self.player = player
        self.damage = damage
        self.cooldown = cooldown
        self.ability_type = ability_type # CLAVE para diferenciar
        
        # --- Lógica de Magnetismo ---
        if ability_type == "magnetism":
            self.radius_multiplier = radius
            base_collection_radius = TILE_SIZE * 3
            self.visual_radius = int(self.radius_multiplier * base_collection_radius)
            self.image = pygame.Surface((self.visual_radius * 2, self.visual_radius * 2), pygame.SRCALPHA)
            self.image.fill((0, 0, 0, 0)) # Transparente, se dibuja en draw_custom
            self.rect = self.image.get_rect(center=self.player.rect.center)
            
        # --- Lógica de Fuego ---
        elif ability_type == "fire":
            # Para fuego, 'radius' es el multiplicador de tamaño de área de daño.
            self.damage_radius_multiplier = radius 
            
            # Cálculo del tamaño (Asegura un tamaño base mínimo de TILE_SIZE * 2)
            self.target_size = int(self.damage_radius_multiplier * (TILE_SIZE * 2)) 
            if self.target_size < TILE_SIZE * 2: 
                self.target_size = TILE_SIZE * 2
            
            self.damage_radius = self.target_size // 2 

            self.original_image_loaded = None 

            try:
                # Carga la imagen de anillo y la escala
                loaded_image = pygame.image.load("assets/sprites/fire_ember.png").convert_alpha() 
                self.original_image_loaded = pygame.transform.scale(loaded_image, (self.target_size, self.target_size))
                self.image = self.original_image_loaded.copy() 
                
            except pygame.error:
                # Fallback con opacidad alta
                print("=====================================================================")
                print("¡ADVERTENCIA! No se encontró 'assets/sprites/fire_ember.png'.")
                print("Usando fallback circular para Aura de Fuego. (Verifique la ruta del archivo)")
                print("=====================================================================")
                
                self.image = pygame.Surface((self.target_size, self.target_size), pygame.SRCALPHA)
                pygame.draw.circle(self.image, (255, 100, 0, 200), (self.damage_radius, self.damage_radius), self.damage_radius)
            
            self.rect = self.image.get_rect(center=self.player.rect.center)
            
        self.last_damage_time = 0
        self.angle = 0 
        
    def update(self):
        """Actualiza la posición y rotación del sprite."""
        
        center_x, center_y = self.player.rect.center
        
        if self.ability_type == "fire" and self.original_image_loaded:
            # Lógica de rotación para Fuego
            self.angle = (self.angle + 3) % 360 
            self.image = pygame.transform.rotate(self.original_image_loaded, self.angle)
            
            # Compensación vertical para el efecto visual
            vertical_offset = TILE_SIZE // 4 
            self.rect = self.image.get_rect(center=(center_x, center_y + vertical_offset))
        
        elif self.ability_type == "fire" and not self.original_image_loaded:
             # Si es fuego pero usa el fallback, solo sigue al jugador (sin offset)
             self.rect.center = (center_x, center_y) 

        elif self.ability_type == "magnetism":
            # Magnetismo solo sigue al jugador
            self.rect.center = (center_x, center_y) 
            
        # NOTA: La lógica de daño de fuego se maneja en main.py (se quitó de aquí)
        
    # Método CLAVE que main.py debe llamar
    def draw_custom(self, surface):
        """Dibuja efectos visuales especiales (como el aura de imán transparente o el fuego)."""
        
        # 1. Dibujar el Aura de Magnetismo (requiere una superficie temporal)
        if self.ability_type == "magnetism":
            temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
            ring_color = (200, 200, 255, 30) 
            
            pygame.draw.circle(
                temp_surface, ring_color, self.rect.center, self.visual_radius
            )
            pygame.draw.circle(
                temp_surface, WHITE, self.rect.center, self.visual_radius, width=2
            )
            surface.blit(temp_surface, (0, 0))

        # 2. Dibujar el Aura de Fuego (se dibuja como un sprite normal)
        elif self.ability_type == "fire":
            surface.blit(self.image, self.rect)