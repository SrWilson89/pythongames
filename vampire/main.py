# main.py
import pygame
import sys
import random
import math
from config import (
    SCREEN_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, 
    BLACK, WHITE, RED, TILE_SIZE
)
from player import Player
from enemies import Enemy
from projectile import Projectile
from bumerang import Bumerang
from area_ability import AreaAbility
from experience_orb import ExperienceOrb
from ui import LevelUpMenu, PauseMenu
from abilities import HABILIDADES_MAESTRAS

# --- Inicialización ---
# Re-inicializamos Pygame para asegurar que esté listo para el bucle principal
pygame.init() 

screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN) 
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# --- Grupos de Sprites ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
bumerangs = pygame.sprite.Group()
area_abilities = pygame.sprite.Group()
orbs = pygame.sprite.Group()

# --- Creación de Objetos ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites.add(player)

# Inicializar Menús
level_up_menu = LevelUpMenu(player)
pause_menu = PauseMenu(screen) 

# --- Variables del Juego ---
last_enemy_spawn = pygame.time.get_ticks() 
SPAWN_RATE = 1000 
game_state = "playing" # Estado: "playing", "paused", "level_up"

# --- Funciones de Lógica ---

def spawn_enemy(last_spawn_time):
    """Genera un enemigo fuera de la pantalla."""
    current_time = pygame.time.get_ticks()
    
    if current_time - last_spawn_time > SPAWN_RATE:
        side = random.choice(["top", "bottom", "left", "right"])
        padding = TILE_SIZE * 2
        
        if side == "top":
            x = random.randint(0, SCREEN_WIDTH)
            y = -padding
        elif side == "bottom":
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + padding
        elif side == "left":
            x = -padding
            y = random.randint(0, SCREEN_HEIGHT)
        else: # right
            x = SCREEN_WIDTH + padding
            y = random.randint(0, SCREEN_HEIGHT)
            
        Enemy(x, y, player, (all_sprites, enemies))
        return current_time # Retorna el nuevo tiempo de spawn
    return last_spawn_time


# --- Bucle Principal del Juego ---
running = True

while running:
    
    current_mouse_pos = pygame.mouse.get_pos()

    # 1. Manejo de Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        # Manejo de la tecla ESCAPE
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            if game_state == "playing" or game_state == "level_up":
                game_state = "paused"
                pause_menu.activate()
            elif game_state == "paused":
                game_state = "playing"
                pause_menu.deactivate()

        # Input del menú de pausa
        if game_state == "paused":
            action = pause_menu.handle_input(event)
            if action == "unpause":
                game_state = "playing"
                pause_menu.deactivate()
            elif action == "quit":
                running = False
                
        # Input del menú de nivel
        elif game_state == "level_up":
            result = level_up_menu.handle_input(event)
            if result == "chosen":
                game_state = "playing"

        # El jugador solo actualiza la posición del ratón si NO estamos en un menú
        if game_state != "level_up":
            player.update_mouse_pos(current_mouse_pos)
            
    # 2. Actualización (Lógica del Juego)
    if game_state == "playing":
        
        # 2a. Spawner de Enemigos
        last_enemy_spawn = spawn_enemy(last_enemy_spawn)
        
        # 2b. Actualización del Jugador y Sprites
        keys = pygame.key.get_pressed()
        
        # --- CORRECCIÓN CLAVE ---
        # 1. ACTUALIZA AL JUGADOR PRIMERO, PASÁNDOLE LAS TECLAS
        attack_info = player.update(keys) 
        
        # 2. ACTUALIZA EL RESTO DE SPRITES
        # Solo actualizamos grupos que NO necesitan argumentos especiales como 'keys'
        enemies.update()
        projectiles.update()
        bumerangs.update()
        area_abilities.update()
        orbs.update()
        
        # 2c. Lanzar Ataques y Habilidades
        if attack_info: 
            if attack_info.get("type") == "AuraFuego":
                if len(area_abilities) == 0:
                    AreaAbility(
                        player, 
                        attack_info["damage"], 
                        attack_info["radius"], 
                        attack_info["cooldown"], 
                        (all_sprites, area_abilities)
                    )

            elif attack_info.get("type") == "Projectile":
                damage = attack_info["damage"]
                directions = attack_info["directions"] 
                
                for direction in directions:
                    Projectile(
                        player.rect.centerx, 
                        player.rect.centery, 
                        direction,
                        damage, 
                        (all_sprites, projectiles)
                    )

            elif attack_info.get("type") == "Bumerang":
                for _ in range(attack_info["count"]):
                    Bumerang(
                        player,
                        attack_info["damage"],
                        attack_info["speed"],
                        attack_info["lifetime"],
                        (all_sprites, bumerangs)
                    )
                    
        # 2d. Chequeo de Colisiones
        hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
        for projectile, hit_enemies in hits.items():
            for enemy in hit_enemies:
                if enemy.take_damage(projectile.damage):
                    ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (all_sprites, orbs))
                    
        pygame.sprite.groupcollide(bumerangs, enemies, False, False)
        
        orb_hits = pygame.sprite.spritecollide(player, orbs, True)
        for orb in orb_hits:
            if player.add_experience(orb.amount):
                game_state = "level_up"
                level_up_menu.activate()


    # 3. Dibujo
    screen.fill(BLACK) 
    all_sprites.draw(screen) 
    
    # Dibujar HUD (Interfaz de usuario)
    font = pygame.font.Font(None, 36)
    text = font.render(f"Nivel: {player.level} | EXP: {player.experience}", True, WHITE)
    screen.blit(text, (10, 10))


    # 4. Dibujar Menús
    if game_state == "level_up":
        level_up_menu.draw(screen)
    elif game_state == "paused":
        pause_menu.draw(screen)
    
    # 5. Finalizar Frame
    pygame.display.flip()
    clock.tick(FPS)

# --- Salida del Juego ---
pygame.quit()
sys.exit()