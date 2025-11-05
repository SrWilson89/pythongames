# main.py

import pygame
import sys
import random
import math 

# Importar todos los módulos creados
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE, BLACK, WHITE
from player import Player
from enemies import Enemy
from ui import LevelUpMenu
from abilities import HABILIDADES_MAESTRAS
from projectile import Projectile
from experience_orb import ExperienceOrb 
from area_ability import AreaAbility 
from bumerang import Bumerang # <-- NUEVA IMPORTACIÓN

# --- Inicialización ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# --- Grupos de Sprites ---
all_sprites = pygame.sprite.Group()
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
experience_orbs = pygame.sprite.Group() 
area_abilities = pygame.sprite.Group() 

# Diccionario de grupos para pasarlo a los enemigos
GAME_GROUPS = {
    'all_sprites': all_sprites,
    'enemies': enemies,
    'projectiles': projectiles,
    'experience_orbs': experience_orbs,
    'area_abilities': area_abilities 
}

# --- Creación de Objetos ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
all_sprites.add(player)

enemy1 = Enemy(100, 100, player, (all_sprites, enemies), GAME_GROUPS) 

# Inicializar el Menú de Nivel
level_up_menu = LevelUpMenu(player)

# ⭐️ LÓGICA DE INICIO: Asignar TRES habilidades iniciales únicas al Nivel 1
ids_disponibles = list(HABILIDADES_MAESTRAS.keys())
if len(ids_disponibles) >= 3:
    habilidades_iniciales = random.sample(ids_disponibles, 3) 
else:
    habilidades_iniciales = ids_disponibles

for h_id in habilidades_iniciales:
    player.active_abilities[h_id] = 1 # Asigna Nivel 1 a las tres

# Inicializar el Aura de Fuego si fue seleccionada
if 3 in player.active_abilities:
    params = HABILIDADES_MAESTRAS[3]["niveles"][0]
    new_aura = AreaAbility(
        player, 
        3, 
        params["damage"], 
        params["radius"], 
        params["cooldown"],
        (all_sprites, area_abilities)
    )
    player.aura_fuego_active = new_aura

# --- Bucle Principal del Juego ---
running = True
last_enemy_spawn = pygame.time.get_ticks() 
SPAWN_RATE = 1000 

while running:
    
    # 1. Manejo de Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if level_up_menu.is_active:
            result = level_up_menu.handle_input(event)
            
            if result == "AuraCreated":
                if player.aura_fuego_active is None:
                    params = HABILIDADES_MAESTRAS[3]["niveles"][0]
                    new_aura = AreaAbility(
                        player, 
                        3, 
                        params["damage"], 
                        params["radius"], 
                        params["cooldown"],
                        (all_sprites, area_abilities)
                    )
                    player.aura_fuego_active = new_aura 
            
    # 2. Actualización (Lógica del Juego)
    if not level_up_menu.is_active:
        
        # 2a. Movimiento y Actualización del Jugador
        keys = pygame.key.get_pressed()
        attack_info = player.update(keys) 

        # 2b. Lanzar Ataques y Habilidades
        if attack_info: 
            if attack_info.get("type") == "AuraFuego":
                 if player.aura_fuego_active:
                     player.aura_fuego_active._update_visuals()

            elif attack_info.get("type") == "Projectile":
                # Daga Rápida
                damage = attack_info["damage"]
                count = attack_info["count"]
                
                for _ in range(count):
                    angle = random.uniform(0, 2 * math.pi) 
                    direction_vector = pygame.math.Vector2(math.cos(angle), math.sin(angle))
                    
                    Projectile(
                        player.rect.centerx, 
                        player.rect.centery, 
                        direction_vector, 
                        damage, 
                        (all_sprites, projectiles)
                    )

            elif attack_info.get("type") == "Bumerang":
                # Bumerán Gigante
                params = attack_info["params"]
                for _ in range(params["count"]):
                    Bumerang(
                        player,
                        params["damage"],
                        params["speed"],
                        params["lifetime"],
                        (all_sprites, projectiles) 
                    )

        # 2c. Actualizar Enemigos, Proyectiles, Orbes y Auras
        enemies.update() 
        projectiles.update() 
        experience_orbs.update(player) 
        area_abilities.update(enemies) 

        # 2d. Spawning de Enemigos
        current_time = pygame.time.get_ticks()
        if current_time - last_enemy_spawn > SPAWN_RATE:
            spawn_x = random.choice([-50, SCREEN_WIDTH + 50])
            spawn_y = random.randint(0, SCREEN_HEIGHT)
            new_enemy = Enemy(spawn_x, spawn_y, player, (all_sprites, enemies), GAME_GROUPS) 
            last_enemy_spawn = current_time

        # 2e. Colisiones (Daño al Enemigo)
        for projectile in projectiles:
            hit_enemies = pygame.sprite.spritecollide(projectile, enemies, False) 
            for enemy in hit_enemies:
                enemy.take_damage(projectile.damage)
                # Solo la Daga (Projectile) se mata al impactar. El Bumerán sigue vivo.
                if isinstance(projectile, Projectile):
                    projectile.kill() 

        # 2f. Colisiones (Recolección de EXP)
        collected_orbs = pygame.sprite.spritecollide(player, experience_orbs, True) 
        for orb in collected_orbs:
            if player.gain_exp(orb.value):
                level_up_menu.activate() 

    # 3. Dibujo
    screen.fill(BLACK) 
    all_sprites.draw(screen) 

    # Dibujar HUD (Interfaz de usuario)
    font_small = pygame.font.Font(None, 20) 
    
    # HUD de Nivel y EXP
    level_text = font_small.render(f"Nivel: {player.level} | EXP: {player.exp}/{player.next_level_exp}", True, WHITE)
    screen.blit(level_text, (10, 10))
    
    # HUD de Habilidades activas
    y_hab = 30
    habilidades_string = "Habilidades: "
    for id_h, nivel in player.active_abilities.items():
        nombre = HABILIDADES_MAESTRAS[id_h]["nombre"]
        habilidades_string += f"{nombre[0]}-Lv{nivel} | " 
    
    if habilidades_string != "Habilidades: ":
        hab_text = font_small.render(habilidades_string, True, WHITE)
        screen.blit(hab_text, (10, y_hab))

    # Dibujar el menú de subida de nivel (si está activo)
    level_up_menu.draw(screen)
    
    # 4. Finalizar Frame
    pygame.display.flip()
    clock.tick(FPS)

# --- Salida del Juego ---
pygame.quit()
sys.exit()