# main.py
import pygame
import sys
import random
import math
import os
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

# ===== DIAGNÓSTICO AUTOMÁTICO DE SPRITES =====
def diagnostic_sprites(screen):
    sprite_dir = "assets/sprites/"
    expected_sprites = {
        "player.png": "Jugador",
        "dagger.png": "Daga",
        "bumerang.png": "Bumerán",
        "ice_shard.png": "Rayo de Escarcha",
        "fire_ring.png": "Aura de Fuego",
        "experience_orb.png": "Orbe EXP",
        "granade.png": "Granada/Bomba"
    }

    results = []
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    results.append(f"=== DIAGNÓSTICO DE SPRITES - {timestamp} ===\n")

    if not os.path.exists(sprite_dir):
        results.append(f"CRÍTICO: '{sprite_dir}' NO EXISTE\n")
    else:
        all_files = os.listdir(sprite_dir)
        results.append(f"Archivos en '{sprite_dir}': {len(all_files)}\n")
        for f in sorted(all_files):
            results.append(f"  • {f}\n")
        results.append("\n")

        loaded_count = 0
        missing_count = 0

        for filename, description in expected_sprites.items():
            path = os.path.join(sprite_dir, filename)
            if os.path.exists(path):
                try:
                    img = pygame.image.load(path).convert_alpha()
                    w, h = img.get_size()
                    results.append(f"CARGADO: {description}: {filename} ({w}x{h})\n")
                    loaded_count += 1
                except Exception as e:
                    results.append(f"FALLÓ: {description}: {filename} | ERROR: {e}\n")
                    missing_count += 1
            else:
                results.append(f"FALTANTE: {description} → {filename}\n")
                missing_count += 1

        results.append("\n")
        results.append(f"RESUMEN: {loaded_count} CARGADOS | {missing_count} PROBLEMAS\n")
        results.append("=" * 60 + "\n")

    try:
        with open("revision.txt", "w", encoding="utf-8") as f:
            f.write("".join(results))
        print(f"DIAGNÓSTICO → 'revision.txt' ({loaded_count}/{len(expected_sprites)})")
    except Exception as e:
        print(f"Error guardando: {e}")

# --- INICIALIZACIÓN ---
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# --- FONDO REPETITIVO DESDE IMAGEN GRANDE (CORREGIDO) ---
TILE_SIZE_BG = 256
bg_tiles = []

def load_background_tiles(path, tile_size):
    try:
        big_img = pygame.image.load(path).convert_alpha()
    except pygame.error:
        print(f"Advertencia: no se encontró {path}")
        return []

    big_w, big_h = big_img.get_size()
    tiles = []
    for y in range(0, big_h, tile_size):
        for x in range(0, big_w, tile_size):
            width  = min(tile_size, big_w - x)
            height = min(tile_size, big_h - y)
            if width <= 0 or height <= 0:
                continue
            rect = pygame.Rect(x, y, width, height)
            tile = big_img.subsurface(rect)
            tiles.append(tile)
    return tiles

bg_tiles = load_background_tiles("Gemini_Generated_Image_uggvxguggvxguggv.png", TILE_SIZE_BG)

def draw_infinite_background(surface, tiles, tile_size, offset_x, offset_y):
    if not tiles:
        surface.fill(BLACK)
        return

    tile = tiles[0]
    sw, sh = surface.get_size()
    cols = -(-sw // tile_size) + 1
    rows = -(-sh // tile_size) + 1

    offset_x %= tile_size
    offset_y %= tile_size

    for row in range(-1, rows):
        for col in range(-1, cols):
            x = col * tile_size - offset_x
            y = row * tile_size - offset_y
            surface.blit(tile, (x, y))

# --- CÁMARA 2D ---
camera = pygame.math.Vector2(0, 0)

def update_camera(target_pos):
    camera.x = target_pos.x - SCREEN_WIDTH // 2
    camera.y = target_pos.y - SCREEN_HEIGHT // 2

def draw_sprite(surface, sprite, camera):
    surface.blit(sprite.image, sprite.rect.move(-camera.x, -camera.y))

# --- GRUPOS DE SPRITES ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
bumerangs = pygame.sprite.Group()
ray_of_frosts = pygame.sprite.Group()
area_abilities = pygame.sprite.Group()
orbs = pygame.sprite.Group()
bombs = pygame.sprite.Group()

# --- OBJETOS ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
player.set_area_group(area_abilities)
level_up_menu = LevelUpMenu(player)
pause_menu = PauseMenu()
game_state = "running"
running = True

# --- PARÁMETROS DE DIFICULTAD ---
WAVE_INTERVAL_MS = 500
WAVE_INTERVAL_FRAMES = max(1, (WAVE_INTERVAL_MS * FPS) // 1000)
wave_timer = 0

# --- HELPER: Obtener aura activa ---
def get_area_ability(ability_type):
    for ability in area_abilities:
        if ability.ability_type == ability_type:
            return ability
    return None

# ==================== BUCLE PRINCIPAL ====================
while running:
    # --- EVENTOS ---
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif game_state == "running" and event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            game_state = "paused"
            pause_menu.activate()
        elif game_state == "paused":
            result = pause_menu.handle_input(event)
            if result == "resume":
                game_state = "running"
            elif result == "quit":
                running = False
        elif game_state == "level_up":
            result = level_up_menu.handle_input(event)
            if result == "closed":
                level_up_menu.deactivate()
                game_state = "running"

    # --- LÓGICA ---
    if game_state == "running":
        # Actualizar sprites
        all_sprites.update()
        enemies.update()
        projectiles.update()
        bumerangs.update()
        ray_of_frosts.update()
        area_abilities.update()
        player.update()
        orbs.update()
        bombs.update()

        # --- ACTUALIZAR CÁMARA ---
        update_camera(player.pos)

        # --- SPAWN DE ENEMIGOS (2 + nivel por 0.5 s, máx 10) ---
        current_enemy_count = len(enemies)
        max_enemies_limit_by_level = min(256, 6 + 2 * player.level)
        spawn_per_half_second = min(10, 2 + player.level)

        if current_enemy_count < max_enemies_limit_by_level:
            wave_timer += 1
            if wave_timer >= WAVE_INTERVAL_FRAMES:
                wave_timer = 0
                enemies_to_spawn = spawn_per_half_second
                available_slots = max_enemies_limit_by_level - current_enemy_count
                num_to_spawn = min(enemies_to_spawn, available_slots)

                for _ in range(num_to_spawn):
                    side = random.choice(["top", "bottom", "left", "right"])
                    if side == "top":
                        x, y = random.randint(0, SCREEN_WIDTH), -TILE_SIZE
                    elif side == "bottom":
                        x, y = random.randint(0, SCREEN_WIDTH), SCREEN_HEIGHT + TILE_SIZE
                    elif side == "left":
                        x, y = -TILE_SIZE, random.randint(0, SCREEN_HEIGHT)
                    else:
                        x, y = SCREEN_WIDTH + TILE_SIZE, random.randint(0, SCREEN_HEIGHT)

                    # VIDA = 10 * nivel del jugador
                    enemy_health_multiplier = player.level
                    Enemy(x, y, player, (all_sprites, enemies), health_multiplier=enemy_health_multiplier)

        # --- ATAQUES ---
        attacks = player.get_attack_data()
        for attack_data in attacks:
            if attack_data["type"] == "Daga Rápida":
                for _ in range(attack_data["count"]):
                    angle = random.uniform(0, 2 * math.pi)
                    direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    Projectile(player.rect.centerx, player.rect.centery, direction, attack_data["damage"], (all_sprites, projectiles))
                player.last_fire_time = pygame.time.get_ticks()

            elif attack_data["type"] == "Rayo de Escarcha":
                closest_enemy = None
                closest_dist = float('inf')
                for enemy in enemies:
                    dist = player.pos.distance_to(enemy.pos)
                    if dist < closest_dist:
                        closest_dist = dist
                        closest_enemy = enemy
                if closest_enemy:
                    dx = closest_enemy.pos.x - player.pos.x
                    dy = closest_enemy.pos.y - player.pos.y
                    dist = math.hypot(dx, dy)
                    direction = pygame.math.Vector2(dx / dist, dy / dist) if dist > 0 else pygame.math.Vector2(1, 0)
                else:
                    angle = random.uniform(0, 2 * math.pi)
                    direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                RayOfFrost(player.rect.centerx, player.rect.centery, direction, attack_data["damage"], (all_sprites, ray_of_frosts))
                player.last_frost_time = pygame.time.get_ticks()

            elif attack_data["type"] == "Aura de Fuego":
                aura = get_area_ability("fire")
                if not aura:
                    # Crear aura con nivel actual
                    nivel = player.active_abilities.get(3, 1)
                    params = HABILIDADES_MAESTRAS[3]["niveles"][nivel - 1]
                    AreaAbility(player, params["damage"], params["radius"], params["cooldown"], (all_sprites, area_abilities), "fire")
                else:
                    # Actualizar aura si el jugador subió de nivel
                    nivel = player.active_abilities.get(3, 1)
                    params = HABILIDADES_MAESTRAS[3]["niveles"][nivel - 1]
                    aura.damage = params["damage"]
                    aura.damage_radius = int(TILE_SIZE * 3 * params["radius"])
                    aura.cooldown = params["cooldown"]

            elif attack_data["type"] == "Bumerang":
                for _ in range(attack_data["count"]):
                    Bumerang(player, attack_data["damage"], attack_data["speed"], attack_data["lifetime"], (all_sprites, bumerangs))
                player.last_bumerang_time = pygame.time.get_ticks()

            elif attack_data["type"] == "Bomba Aleatoria":
                for _ in range(attack_data["count"]):
                    offset_x = random.randint(-200, 200)
                    offset_y = random.randint(-200, 200)
                    Bomb(player.rect.centerx + offset_x, player.rect.centery + offset_y,
                         attack_data["damage"], attack_data["radius"], attack_data["fall_time"],
                         (all_sprites, bombs), orbs)
                player.last_bomb_time = pygame.time.get_ticks()

        # --- COLISIONES ---
        hits_proj = pygame.sprite.groupcollide(projectiles, enemies, True, False)
        for proj, hit_enemies in hits_proj.items():
            for enemy in hit_enemies:
                if enemy.take_damage(proj.damage):
                    ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))

        hits_rays = pygame.sprite.groupcollide(ray_of_frosts, enemies, True, False)
        for ray, hit_enemies in hits_rays.items():
            for enemy in hit_enemies:
                if enemy.take_damage(ray.damage):
                    ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))

        hits_bumerangs = pygame.sprite.groupcollide(bumerangs, enemies, False, False)
        for bumerang, hit_enemies in hits_bumerangs.items():
            if not bumerang.has_hit:
                for enemy in hit_enemies:
                    if enemy.take_damage(bumerang.damage):
                        ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))
                bumerang.has_hit = True

        # --- COLISIÓN ENEMIGO-JUGADOR ---
        enemy_player_hits = pygame.sprite.spritecollide(player, enemies, True)
        for enemy in enemy_player_hits:
            player.take_damage(1)
            ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))

        aura = get_area_ability("fire")
        if aura:
            current_time = pygame.time.get_ticks()
            if current_time - aura.last_damage_time >= aura.cooldown:
                aura.last_damage_time = current_time
                for enemy in enemies:
                    if enemy.pos.distance_to(player.pos) < aura.damage_radius:
                        if enemy.take_damage(aura.damage):
                            ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs,))

        for orb in orbs:
            orb.set_target(player, magnetism_aura_radius=1.0)
        orb_hits = pygame.sprite.spritecollide(player, orbs, True)
        for orb in orb_hits:
            if player.add_experience(orb.amount):
                if obtener_opciones_subida_nivel(player.active_abilities):
                    game_state = "level_up"
                    level_up_menu.activate()

    # --- DIBUJO ---
    draw_infinite_background(screen, bg_tiles, TILE_SIZE_BG, camera.x, camera.y)

    # --- DIBUJAR SPRITES CON CÁMARA ---
    for enemy in enemies:
        draw_sprite(screen, enemy, camera)
    draw_sprite(screen, player, camera)
    for orb in orbs:
        draw_sprite(screen, orb, camera)
    for proj in projectiles:
        draw_sprite(screen, proj, camera)
    for ray in ray_of_frosts:
        draw_sprite(screen, ray, camera)
    for bum in bumerangs:
        draw_sprite(screen, bum, camera)
    for bomb in bombs:
        screen.blit(bomb.image, bomb.rect.move(-camera.x, -camera.y))
    for ability in area_abilities:
        screen.blit(ability.image, ability.rect.move(-camera.x, -camera.y))

    if game_state == "running":
        for enemy in enemies:
            bar_x = enemy.rect.centerx - camera.x
            bar_y = enemy.rect.top - camera.y - 10
            bar_w = TILE_SIZE * 0.8
            bar_h = 5
            fill = (enemy.health / enemy.max_health) * bar_w
            pygame.draw.rect(screen, (255, 0, 0), (bar_x - bar_w // 2, bar_y, bar_w, bar_h))
            pygame.draw.rect(screen, (0, 255, 0), (bar_x - bar_w // 2, bar_y, fill, bar_h))
            pygame.draw.rect(screen, (255, 255, 255), (bar_x - bar_w // 2, bar_y, bar_w, bar_h), 1)

    # --- HUD ---
    font = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 30)
    y_hud = 10
    screen.blit(font.render(f"Nivel: {player.level} | EXP: {player.experience}", True, WHITE), (10, y_hud))
    y_hud += 30
    screen.blit(font.render(f"HP: {player.health}/{player.max_health}", True, RED), (10, y_hud))

    current_enemy_count = len(enemies)
    max_enemies_limit_by_level = min(256, 6 + 2 * player.level)
    enemy_text = font.render(f"ENEMIGOS: {current_enemy_count}/{max_enemies_limit_by_level}", True, WHITE)
    screen.blit(enemy_text, (SCREEN_WIDTH - enemy_text.get_width() - 10, 10))

    screen.blit(font.render("HABILIDADES ACTIVAS:", True, WHITE), (10, SCREEN_HEIGHT - 130))
    y_abil = SCREEN_HEIGHT - 100
    for hid, lvl in player.active_abilities.items():
        if hid in HABILIDADES_MAESTRAS:
            name = HABILIDADES_MAESTRAS[hid]["nombre"]
            txt = font_small.render(f"- {name} (Nv. {lvl})", True, WHITE)
            screen.blit(txt, (20, y_abil))
            y_abil += 25

    if game_state == "level_up":
        level_up_menu.draw(screen)
    elif game_state == "paused":
        pause_menu.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()