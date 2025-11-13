# main.py - VERSIÓN COMPLETA Y CORREGIDA

import pygame
import sys
import random
import math
import os
from datetime import datetime

# --- Importaciones de Configuración ---
from config import (
    SCREEN_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    BLACK, WHITE, RED, TILE_SIZE,
    EXPERIENCE_PER_LEVEL 
)

# --- Importaciones de Clases del Juego ---
from player import Player
from enemies import Enemy
from projectile import Projectile
from bumerang import Bumerang
from ray_of_frost import RayOfFrost
from area_ability import AreaAbility
from experience_orb import ExperienceOrb
from ui import LevelUpMenu, PauseMenu
from abilities import HABILIDADES_MAESTRAS, obtener_opciones_subida_nivel
from bomb import Bomb

import os
import sys

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA (Añadida para PyInstaller)
# =======================================================
def resource_path(relative_path):
    """
    Función que maneja rutas de recursos para desarrollo local o
    ejecutables empaquetados por PyInstaller.
    """
    try:
        # sys._MEIPASS es la carpeta temporal creada por PyInstaller
        base_path = sys._MEIPASS
    except Exception:
        # Cuando se ejecuta localmente (en desarrollo)
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# =======================================================

# ===== DIAGNÓSTICO AUTOMÁTICO DE SPRITES (Útil para depuración) =====
def diagnostic_sprites(screen):
    # (Tu lógica de diagnóstico aquí)
    pass
# ====================================================================

# --- Inicialización de Pygame ---
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()
random.seed(datetime.now().timestamp())
font = pygame.font.Font(None, 36)

# --- Grupos de Sprites ---
all_sprites = pygame.sprite.Group() # Contiene sprites que necesitan el offset (Jugador, Enemigos, Habilidades de Área)
projectiles = pygame.sprite.Group() # Proyectiles que dañan enemigos
enemies = pygame.sprite.Group()     # Enemigos
orbs = pygame.sprite.Group()        # Orbes de experiencia
bombs = pygame.sprite.Group()       # Bombas y explosiones
area_abilities = pygame.sprite.Group() # Habilidades de área (como el aura de fuego)

# --- Inicialización del Jugador ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites.add(player)

# Asignar grupos al jugador para que pueda spawnear objetos
player.orbs_group = orbs
player.projectiles_group = projectiles
player.enemies_group = enemies 
player.all_sprites_group = all_sprites # Añadido si necesitas grupos completos

# --- Variables del Juego ---
game_state = "running" # Puede ser "running", "paused", "level_up"
current_enemy_count = 0
max_enemies_limit = 256
last_spawn_time = pygame.time.get_ticks()
spawn_cooldown = 200 # ms entre spawn y spawn

# --- Menús ---
level_up_menu = LevelUpMenu(player)
pause_menu = PauseMenu()

# --- CAMARA / OFFSET ---
offset = pygame.math.Vector2(0, 0) 

# --- GENERACIÓN DE ENEMIGOS ---
def spawn_enemy():
    """Genera un enemigo aleatorio fuera de la pantalla."""
    
    max_enemies_limit_by_level = min(max_enemies_limit, 8 * player.level)
    
    if len(enemies) >= max_enemies_limit_by_level:
        return 
        
    side = random.choice(['top', 'bottom', 'left', 'right'])
    player_center = player.rect.center
    
    if side == 'top':
        x = player_center[0] + random.randint(-SCREEN_WIDTH // 2, SCREEN_WIDTH // 2)
        y = player_center[1] - SCREEN_HEIGHT // 2 - TILE_SIZE
    elif side == 'bottom':
        x = player_center[0] + random.randint(-SCREEN_WIDTH // 2, SCREEN_WIDTH // 2)
        y = player_center[1] + SCREEN_HEIGHT // 2 + TILE_SIZE
    elif side == 'left':
        x = player_center[0] - SCREEN_WIDTH // 2 - TILE_SIZE
        y = player_center[1] + random.randint(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2)
    elif side == 'right':
        x = player_center[0] + SCREEN_WIDTH // 2 + TILE_SIZE
        y = player_center[1] + random.randint(-SCREEN_HEIGHT // 2, SCREEN_HEIGHT // 2)
        
    health_mult = 1.0 + (player.level - 1) * 0.2 
    
    # Crear y añadir el enemigo. Se añade a all_sprites y enemies.
    Enemy(x, y, player, (all_sprites, enemies), health_multiplier=health_mult)


# --- LÓGICA DE COLISIONES ---
def check_collisions():
    """Maneja todas las interacciones de colisión en el juego."""
    
    # 1. Proyectiles (Dagas, Rayos) vs Enemigos
    for proj in projectiles:
        # Colisión con un solo enemigo (True para eliminar el proyectil)
        hit_list = pygame.sprite.spritecollide(proj, enemies, False) 
        if hit_list:
            enemy = hit_list[0]
            if enemy.take_damage(proj.damage):
                ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))
            proj.kill() 

    # 2. Bumerangs vs Enemigos (asumiendo que bumerangs tiene un grupo)
    # Debes usar el nombre correcto del grupo que contiene los bumerangs
    # Asumimos que los bumerangs están en 'projectiles' o un grupo dedicado 'bumerang_group'
    # Si están en 'projectiles', la lógica ya está cubierta arriba.
    
    # 3. Habilidades de Área (Aura de Fuego) vs Enemigos
    for ability in area_abilities:
        ability.check_damage(enemies)

    # 4. Orbes vs Jugador 
    for orb in orbs:
        orb.set_target(player) # Activa el imán
        if pygame.sprite.collide_rect(orb, player):
             player.add_experience(orb.amount)
             orb.kill()
             
    # 5. Enemigos vs Jugador
    hit_enemies = pygame.sprite.spritecollide(player, enemies, False) 
    for enemy in hit_enemies:
        player.take_damage(5) 


# --- Bucle Principal del Juego ---
running = True
while running:
    clock.tick(FPS)
    current_time = pygame.time.get_ticks()

    # Manejo de Eventos (Pausa, Salir, Menús)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "running":
                    game_state = "paused"
                    pause_menu.activate()
                elif game_state == "paused":
                    game_state = "running"
                    pause_menu.deactivate()
            
            if game_state == "level_up":
                selection = level_up_menu.handle_keyboard_input(event)
                if selection is not None:
                    # Aplicar la mejora y reanudar el juego
                    hid, type = selection
                    groups_to_pass = all_sprites # Pasamos all_sprites para que el aura se añada al grupo principal
                    if type == "Nueva":
                        player.add_new_ability(hid, groups_to_pass) 
                    else:
                        player.upgrade_ability(hid, groups_to_pass) 
                    
                    level_up_menu.deactivate()
                    game_state = "running"

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            
            if game_state == "paused":
                action = pause_menu.handle_click(mouse_pos)
                if action == "resume":
                    game_state = "running"
                    pause_menu.deactivate()
                elif action == "quit":
                    running = False
                    
            elif game_state == "level_up":
                selection = level_up_menu.handle_click(mouse_pos)
                if selection is not None:
                    # Aplicar la mejora y reanudar el juego
                    hid, type = selection
                    groups_to_pass = all_sprites # Pasamos all_sprites para el aura
                    if type == "Nueva":
                        player.add_new_ability(hid, groups_to_pass) 
                    else:
                        player.upgrade_ability(hid, groups_to_pass) 
                        
                    level_up_menu.deactivate()
                    game_state = "running"


    # --- Lógica de Actualización (Update Logic) ---
    if game_state == "running":
        
        # 1. Movimiento del Jugador y Otros Sprites
        keys = pygame.key.get_pressed() 
        player.update(keys)             # <--- Correcto: Llama con 'keys'

        # all_sprites.update()          # <--- ¡ESTA LÍNEA SE HA ELIMINADO PARA ARREGLAR EL ERROR!
        
        # Actualizar los grupos que quedan (enemigos, proyectiles, etc.)
        enemies.update()
        projectiles.update()
        orbs.update()
        bombs.update()
        area_abilities.update()
        
        # 2. Movimiento de la Cámara (Offset)
        offset.x = player.rect.centerx - SCREEN_WIDTH // 2
        offset.y = player.rect.centery - SCREEN_HEIGHT // 2
        
        # 3. Lógica de Colisiones
        check_collisions()
        
        # 4. Generación de Enemigos
        if current_time - last_spawn_time > spawn_cooldown:
            spawn_enemy()
            last_spawn_time = current_time
            
        # 5. Lógica de Subida de Nivel
        if player.experience >= player.level * EXPERIENCE_PER_LEVEL:
            player.level += 1
            player.experience = 0 
            game_state = "level_up"
            level_up_menu.activate()


    # --- Lógica de Dibujo (Draw Logic) ---
    screen.fill(BLACK)

    # 1. Dibujar el Mapa/Fondo
    map_size = TILE_SIZE * 100 
    map_rect = pygame.Rect(-map_size // 2, -map_size // 2, map_size, map_size)
    draw_rect = map_rect.move(-offset.x, -offset.y)
    pygame.draw.rect(screen, (20, 20, 20), draw_rect)
    
    # 2. Dibujar Sprites (usando el offset)
    
    # Enemigos
    for enemy in enemies:
        draw_pos = enemy.rect.topleft - offset
        screen.blit(enemy.image, draw_pos)
            
    # Orbes y Proyectiles
    for orb in orbs: 
        draw_pos = orb.rect.topleft - offset
        screen.blit(orb.image, draw_pos)

    for proj in projectiles: 
        draw_pos = proj.rect.topleft - offset
        screen.blit(proj.image, draw_pos)
        
    # Sprites con lógica de dibujo personalizada (deben recibir el offset)
    for bomb in bombs:
        bomb.draw_custom(screen, offset) 
        
    for ability in area_abilities:
        ability.draw_custom(screen, offset) 

    # Dibujar al jugador (para que esté siempre encima)
    draw_pos = player.rect.topleft - offset
    screen.blit(player.image, draw_pos)

    # Barras de Vida (siempre dibujadas en 'running' o 'paused')
    if game_state == "running" or game_state == "paused":
        for enemy in enemies:
            enemy.draw_health_bar(screen, offset) 

    # --- HUD ---
    y_hud = 10
    screen.blit(font.render(f"Nivel: {player.level} | EXP: {player.experience}/{player.level * EXPERIENCE_PER_LEVEL}", True, WHITE), (10, y_hud))
    y_hud += 30
    hp_color = RED if player.health < player.max_health * 0.3 else WHITE
    screen.blit(font.render(f"HP: {player.health}/{player.max_health}", True, hp_color), (10, y_hud))

    current_enemy_count = len(enemies)
    max_enemies_limit_by_level = min(max_enemies_limit, 8 * player.level)
    enemy_text = font.render(f"ENEMIGOS: {current_enemy_count}/{max_enemies_limit_by_level}", True, WHITE)
    screen.blit(enemy_text, (SCREEN_WIDTH - enemy_text.get_width() - 10, 10))

    # HUD de Habilidades
    screen.blit(font.render("HABILIDADES ACTIVAS:", True, WHITE), (10, SCREEN_HEIGHT - 130))
    font_small = pygame.font.Font(None, 30)
    y_abil = SCREEN_HEIGHT - 100
    for hid, lvl in player.active_abilities.items():
        if hid in HABILIDADES_MAESTRAS:
            nombre = HABILIDADES_MAESTRAS[hid]["nombre"]
            text = font_small.render(f"{nombre}: Nv.{lvl}", True, WHITE)
            screen.blit(text, (10, y_abil))
            y_abil += 25

    # --- Dibujar Menús (Siempre encima de todo) ---
    if game_state == "paused":
        pause_menu.draw(screen)
    elif game_state == "level_up":
        level_up_menu.draw(screen)

    pygame.display.flip()

pygame.quit()
sys.exit()