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
            f.write("\n".join(results))
        print(f"DIAGNÓSTICO → 'revision.txt' ({loaded_count}/{len(expected_sprites)})")
    except Exception as e:
        print(f"Error guardando: {e}")

# --- INICIALIZACIÓN ---
pygame.init()
screen = pygame.display.set_mode(SCREEN_SIZE)
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# DIAGNÓSTICO
diagnostic_sprites(screen)

# --- FONDO ---
BACKGROUND_IMAGE_NAME = "Gemini_Generated_Image_uggvxguggvxguggv.png"
BACKGROUND_IMAGE = None
try:
    original_bg = pygame.image.load(BACKGROUND_IMAGE_NAME).convert()
    BACKGROUND_IMAGE = pygame.transform.scale(original_bg, SCREEN_SIZE)
    print(f"Fondo '{BACKGROUND_IMAGE_NAME}' cargado.")
except pygame.error:
    print(f"Fondo no encontrado. Usando negro.")

# --- GRUPOS DE SPRITES ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()      # Dagas
bumerangs = pygame.sprite.Group()        # Bumerán
ray_of_frosts = pygame.sprite.Group()    # Rayo de Escarcha
area_abilities = pygame.sprite.Group()   # Aura de Fuego
orbs = pygame.sprite.Group()             # Orbes de EXP
bombs = pygame.sprite.Group()            # Bombas

# --- OBJETOS ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
level_up_menu = LevelUpMenu(player)
pause_menu = PauseMenu()
game_state = "running"
running = True

# --- PARÁMETROS DE DIFICULTAD ---
MAX_ENEMIES_LIMIT = 256
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

        # --- SPAWN DE ENEMIGOS ---
        current_enemy_count = len(enemies)
        enemy_health_multiplier = 2.0 if current_enemy_count >= MAX_ENEMIES_LIMIT else 1.0
        wave_timer += 1
        if wave_timer >= WAVE_INTERVAL_FRAMES:
            wave_timer = 0
            enemies_to_spawn = 2 ** player.level
            max_spawnable = MAX_ENEMIES_LIMIT - current_enemy_count
            num_to_spawn = max(0, min(enemies_to_spawn, max_spawnable))

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
                Enemy(x, y, player, (all_sprites, enemies), health_multiplier=enemy_health_multiplier)

        # --- ATAQUES MÚLTIPLES ---
        attacks = player.get_attack_data()
        for attack_data in attacks:
            print(f"ATACANDO: {attack_data['type']}")  # DEBUG

            if attack_data["type"] == "Daga Rápida":
                for _ in range(attack_data["count"]):
                    angle = random.uniform(0, 2 * math.pi)
                    direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    Projectile(player.rect.centerx, player.rect.centery, direction, attack_data["damage"], (all_sprites, projectiles))
                player.last_fire_time = pygame.time.get_ticks()

            elif attack_data["type"] == "Rayo de Escarcha":
                # AUTOMÁTICO: hacia el enemigo más cercano
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
                    # Fallback: dirección aleatoria
                    angle = random.uniform(0, 2 * math.pi)
                    direction = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                
                RayOfFrost(player.rect.centerx, player.rect.centery, direction, attack_data["damage"], (all_sprites, ray_of_frosts))
                player.last_frost_time = pygame.time.get_ticks()

            elif attack_data["type"] == "Aura de Fuego":
                if not get_area_ability("fire"):
                    AreaAbility(player, attack_data["damage"], attack_data["radius"], attack_data["cooldown"], (all_sprites, area_abilities), "fire")

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
    if BACKGROUND_IMAGE:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
    else:
        screen.fill(BLACK)

    enemies.draw(screen)
    screen.blit(player.image, player.rect)
    orbs.draw(screen)
    projectiles.draw(screen)
    ray_of_frosts.draw(screen)
    bumerangs.draw(screen)

    for bomb in bombs:
        bomb.draw_custom(screen)

    for ability in area_abilities:
        ability.draw_custom(screen)

    if game_state == "running":
        for enemy in enemies:
            enemy.draw_health_bar(screen)

    # --- HUD ---
    font = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 30)
    y_hud = 10
    screen.blit(font.render(f"Nivel: {player.level} | EXP: {player.experience}", True, WHITE), (10, y_hud))
    y_hud += 30
    screen.blit(font.render(f"HP: {player.health}/{player.max_health}", True, RED), (10, y_hud))

    current_enemy_count = len(enemies)
    enemy_health_multiplier = 2.0 if current_enemy_count >= MAX_ENEMIES_LIMIT else 1.0
    diff_text = f" | Dificultad: x{int(enemy_health_multiplier)}" if enemy_health_multiplier > 1 else ""
    enemy_text = font.render(f"ENEMIGOS: {current_enemy_count}/{MAX_ENEMIES_LIMIT}{diff_text}", True, WHITE)
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