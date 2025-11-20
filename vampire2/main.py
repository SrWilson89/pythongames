# main.py
import pygame
import sys
import random
import math
import os
import logging 
from datetime import datetime
from config import (
    SCREEN_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    BLACK, WHITE, RED, TILE_SIZE
)
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

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA (Necesaria para PyInstaller)
# =======================================================
def resource_path(relative_path):
    """
    Función que maneja rutas de recursos para desarrollo local o
    ejecutables empaquetados por PyInstaller.
    """
    try:
        # sys._MEIPASS es la ruta de la carpeta temporal que PyInstaller crea
        base_path = sys._MEIPASS
    except Exception:
        # Si no está empaquetado (se ejecuta localmente), usa la ruta actual
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# =======================================================
# BLOQUE DE LOGGING PARA DIAGNÓSTICO DE ERRORES (CLAVE)
# =======================================================
log_path = os.path.join(os.path.abspath("."), "error_log.txt")
logging.basicConfig(filename=log_path, 
                    level=logging.ERROR,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def log_unhandled_exception(exc_type, exc_value, exc_traceback):
    """Manejador global de excepciones para registrar errores no capturados."""
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return

    logging.error("Excepción no controlada", exc_info=(exc_type, exc_value, exc_traceback))

sys.excepthook = log_unhandled_exception

# =======================================================
# INICIALIZACIÓN DE PYGAME Y JUEGO
# =======================================================

pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE, pygame.FULLSCREEN)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# Grupos de Sprites
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
orbs = pygame.sprite.Group()
bombs = pygame.sprite.Group()
bumerangs = pygame.sprite.Group()
area_abilities = pygame.sprite.Group()

# Jugador y Menús
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
player.set_area_group(area_abilities) 
all_sprites.add(player)
level_up_menu = LevelUpMenu(player)
pause_menu = PauseMenu()

game_state = "running"
running = True

# --- CARGA DEL FONDO EN MOSAICO ---
try:
    BACKGROUND_TILE = pygame.image.load(resource_path("assets/background/tile.png")).convert()
except pygame.error:
    BACKGROUND_TILE = pygame.Surface((TILE_SIZE * 4, TILE_SIZE * 4))
    BACKGROUND_TILE.fill((50, 50, 50)) # Gris oscuro de fallback
    print("Advertencia: No se pudo cargar assets/background/tile.png. Usando un fondo gris.")
# --- FIN CARGA DE FONDO ---

WAVE_INTERVAL_FRAMES = max(1, (500 * FPS) // 1000)
enemy_spawn_timer = 0
current_wave_multiplier = 1.0

# Bucle Principal del Juego
while running:
    # Manejo de Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if game_state == "running":
                    game_state = "paused"
                elif game_state == "paused":
                    game_state = "running"
                elif game_state == "level_up":
                    game_state = "paused"
            
            if game_state == "level_up":
                level_up_menu.handle_input(event.key)
            elif game_state == "paused":
                action = pause_menu.handle_input(event.key) 
                if action == "resume":
                    game_state = "running"
                elif action == "quit":
                    running = False

    # Lógica del Juego
    if game_state == "running":
        # --- Actualizaciones ---
        player.update()
        
        # ... (Toda la lógica de juego anterior) ...
        # (Se asume que la lógica de spawn, colisiones y ataques está correcta)
        # ...

        enemies.update()
        projectiles.update()
        bumerangs.update()
        orbs.update()
        area_abilities.update()
        
        # Colisiones de Proyectiles/Bumerang/Bombas
        # ... (Mantener la lógica de colisiones) ...
        for projectile in projectiles:
             hit_list = pygame.sprite.spritecollide(projectile, enemies, False)
             if hit_list:
                 for enemy in hit_list:
                     if enemy.take_damage(projectile.damage):
                          ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))
                 projectile.kill()
        
        for bumerang in bumerangs:
             hit_enemies = bumerang.check_hit(enemies)
             for enemy in hit_enemies:
                 if enemy.take_damage(bumerang.damage):
                     ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))
        
        for ability in area_abilities:
            ability.check_damage(enemies)
        
        # Colisiones de Jugador/Orbes
        for orb in orbs:
            orb.set_target(player) 
        collected_orbs = pygame.sprite.spritecollide(player, orbs, True)
        for orb in collected_orbs:
            player.add_experience(orb.amount)

        # Colisiones de Enemigos/Jugador
        hit_enemies = pygame.sprite.spritecollide(player, enemies, False)
        if hit_enemies:
            player.take_damage(1) 
        
        # Comprobar si sube de nivel
        if player.should_level_up():
            game_state = "level_up"
            player.level_up() 
            level_up_menu.activate() 
    
    # ... (Lógica de menus) ...
    elif game_state == "level_up":
        selected_id = level_up_menu.handle_mouse_click(pygame.mouse.get_pos())
        if selected_id is not None:
            hid, tipo = selected_id
            if tipo == "Nueva":
                player.add_new_ability(hid)
            else:
                player.upgrade_ability(hid)
            game_state = "running"
            
    elif game_state == "paused":
        action = pause_menu.handle_mouse_click(pygame.mouse.get_pos())
        if action == "resume":
            game_state = "running"
        elif action == "quit":
            running = False

    # --- Dibujo ---
    screen.fill(BLACK) # Se mantiene el relleno negro

    # CÁLCULO DEL OFFSET (Cámara)
    offset = pygame.math.Vector2(player.rect.centerx - SCREEN_WIDTH // 2, player.rect.centery - SCREEN_HEIGHT // 2)

    # 1. DIBUJO DEL FONDO EN MOSAICO (TILING)
    tile_w = BACKGROUND_TILE.get_width()
    tile_h = BACKGROUND_TILE.get_height()
    
    # Calcular el desplazamiento inicial para que el mosaico se sienta anclado al mundo
    start_x = - (offset.x % tile_w)
    start_y = - (offset.y % tile_h)
    
    # Dibujar los mosaicos
    for x in range(int(start_x - tile_w), SCREEN_WIDTH + tile_w, tile_w):
        for y in range(int(start_y - tile_h), SCREEN_HEIGHT + tile_h, tile_h):
            screen.blit(BACKGROUND_TILE, (x, y))


    # 2. DIBUJO DE SPRITES (Aplicando el offset)
    for sprite in all_sprites:
        # El jugador y los enemigos (todos los que están en all_sprites)
        screen.blit(sprite.image, sprite.rect.move(-offset.x, -offset.y))

    # Proyectiles, Orbes (no están en all_sprites, necesitan ser dibujados con offset)
    for sprite in projectiles:
         screen.blit(sprite.image, sprite.rect.move(-offset.x, -offset.y))
    for sprite in orbs:
         screen.blit(sprite.image, sprite.rect.move(-offset.x, -offset.y))
    for sprite in bumerangs:
         screen.blit(sprite.image, sprite.rect.move(-offset.x, -offset.y))


    # 3. Habilidades con dibujo especial (DEBEN RECIBIR Y USAR EL OFFSET)
    for bomb in bombs:
        bomb.draw_custom(screen, offset) 
    for ability in area_abilities:
        ability.draw_custom(screen, offset) 

    # 4. Barras de Vida (DEBEN RECIBIR Y USAR EL OFFSET)
    if game_state == "running":
        for enemy in enemies:
            enemy.draw_health_bar(screen, offset) 

    # 5. HUD (Sin offset)
    font = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 30)
    # ... (Dibujo de HUD) ...
    y_hud = 10
    screen.blit(font.render(f"Nivel: {player.level} | EXP: {player.experience}", True, WHITE), (10, y_hud))
    y_hud += 30
    screen.blit(font.render(f"HP: {player.health}/{player.max_health}", True, RED), (10, y_hud))

    current_enemy_count = len(enemies)
    max_enemies_limit_by_level = min(256, 8 * player.level)
    enemy_text = font.render(f"ENEMIGOS: {current_enemy_count}/{max_enemies_limit_by_level}", True, WHITE)
    screen.blit(enemy_text, (SCREEN_WIDTH - enemy_text.get_width() - 10, 10))

    screen.blit(font.render("HABILIDADES ACTIVAS:", True, WHITE), (10, SCREEN_HEIGHT - 130))
    y_abil = SCREEN_HEIGHT - 100
    for hid, lvl in player.active_abilities.items():
        if hid in HABILIDADES_MAESTRAS:
            nombre = HABILIDADES_MAESTRAS[hid]["nombre"]
            text = font_small.render(f"{nombre} (Nv. {lvl})", True, WHITE)
            screen.blit(text, (20, y_abil))
            y_abil += 30
            
    # Menús
    if game_state == "level_up":
        level_up_menu.draw(screen)
    elif game_state == "paused":
        pause_menu.draw(screen)
        
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()