# enemies.py

import pygame
from config import TILE_SIZE, GREEN, RED, BLACK
from experience_orb import ExperienceOrb 

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, player, groups_to_join, game_groups_ref): 
        super().__init__(groups_to_join) 

        # 1. Configuración Visual (Pixel Art)
        try:
            # CORRECCIÓN: Usar convert_alpha() para transparencia
            self.image = pygame.image.load("assets/sprites/enemy.png").convert_alpha()
            self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE))
        except pygame.error:
            self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
            self.image.fill(RED) 
            
        self.rect = self.image.get_rect(topleft=(x, y))

        # 2. Estadísticas
        self.speed = 1
        self.health = 5
        self.exp_value = 1 
        self.player = player 
        self.game_groups_ref = game_groups_ref 

    def update(self):
        """Mueve al enemigo hacia la posición del jugador."""
        
        player_pos = self.player.rect.center
        
        dx = player_pos[0] - self.rect.centerx
        dy = player_pos[1] - self.rect.centery
        
        dist = (dx**2 + dy**2)**0.5
        
        if dist > 0:
            self.rect.x += (dx / dist) * self.speed
            self.rect.y += (dy / dist) * self.speed

    def take_damage(self, damage):
        self.health -= damage
        if self.health <= 0:
            self.kill() 
            # Generar el orbe de EXP al morir
            ExperienceOrb(
                self.rect.centerx, 
                self.rect.centery, 
                self.exp_value, 
                (self.game_groups_ref.get('all_sprites'), self.game_groups_ref.get('experience_orbs')) 
            )