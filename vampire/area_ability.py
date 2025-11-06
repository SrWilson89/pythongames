# area_ability.py
import pygame
import math
from config import RED, TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT

# Define un tamaño base para el emoji/texto
EMOJI_SIZE = TILE_SIZE // 2 

class AreaAbility(pygame.sprite.Sprite):
    def __init__(self, player, damage, radius, cooldown, groups):
        super().__init__(groups)
        self.player = player
        self.damage = damage
        self.cooldown = cooldown
        # Escalar el radio para que sea visible
        self.radius = radius * (TILE_SIZE // 32)
        
        # Inicialización del sprite
        # Creamos una superficie transparente lo suficientemente grande para el radio
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), pygame.SRCALPHA)
        self.rect = self.image.get_rect(center=self.player.rect.center)
        
        self.last_damage_time = 0
        self.angle = 0 # Ángulo de rotación para el emoji
        
        # Fuente para dibujar el emoji (requiere que el sistema tenga fuentes emoji)
        self.font = pygame.font.Font(None, EMOJI_SIZE) 
        self.flame_emoji = self.font.render("🔥", True, (255, 255, 255)) # El color no importa mucho para emojis
        self.emoji_rect = self.flame_emoji.get_rect()


    def update(self):
        """Actualiza la posición, el emoji giratorio y aplica daño."""
        
        # 1. Mover el centro del área al centro del jugador
        self.rect.center = self.player.rect.center
        
        # 2. Lógica de Rotación y Dibujo del Emoji
        self.image.fill((0, 0, 0, 0)) # Limpiar el frame anterior
        self.angle = (self.angle + 5) % 360 # Rotar 5 grados por frame
        
        # Calcular la posición del emoji en el borde del radio
        rads = math.radians(self.angle)
        emoji_x = self.radius + self.radius * math.cos(rads)
        emoji_y = self.radius + self.radius * math.sin(rads)
        
        # Centrar el emoji
        self.emoji_rect.center = (int(emoji_x), int(emoji_y))
        
        # Dibujar el emoji en la superficie de la habilidad
        self.image.blit(self.flame_emoji, self.emoji_rect)
        
        # 3. Lógica de Daño (se mantiene igual)
        current_time = pygame.time.get_ticks()
        if current_time - self.last_damage_time > self.cooldown:
            # Aquí iría la lógica para dañar enemigos dentro del radio
            self.last_damage_time = current_time