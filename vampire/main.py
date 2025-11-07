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
from ray_of_frost import RayOfFrost
from area_ability import AreaAbility 
from experience_orb import ExperienceOrb
from ui import LevelUpMenu, PauseMenu
from abilities import HABILIDADES_MAESTRAS, obtener_opciones_subida_nivel

# --- Inicialización ---
pygame.init() 
screen = pygame.display.set_mode(SCREEN_SIZE) 
pygame.display.set_caption(TITLE)
clock = pygame.time.Clock()

# --- Carga del Fondo ---
BACKGROUND_IMAGE_NAME = "Gemini_Generated_Image_uggvxguggvxguggv.png"
BACKGROUND_IMAGE = None
try:
    # Intenta cargar la imagen en la raíz del proyecto
    original_bg = pygame.image.load(BACKGROUND_IMAGE_NAME).convert()
    BACKGROUND_IMAGE = pygame.transform.scale(original_bg, SCREEN_SIZE)
    print(f"Fondo '{BACKGROUND_IMAGE_NAME}' cargado correctamente.")
except pygame.error:
    print(f"ADVERTENCIA: No se pudo cargar el fondo '{BACKGROUND_IMAGE_NAME}'. Asegúrese de que el archivo está en la carpeta raíz del juego. Usando color negro.")

# --- Grupos de Sprites ---
all_sprites = pygame.sprite.Group() 
enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
bumerangs = pygame.sprite.Group()
ray_of_frosts = pygame.sprite.Group() 
area_abilities = pygame.sprite.Group()
orbs = pygame.sprite.Group()

# --- Creación de Objetos ---
player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)

# --- UI y Estado ---
level_up_menu = LevelUpMenu(player)
pause_menu = PauseMenu()
game_state = "running"
running = True

# --- Lógica de Juego y Timers ---
last_fire_damage_time = 0 

# --- PARÁMETROS DE DIFICULTAD Y OLAS ---
MAX_ENEMIES_LIMIT = 256
WAVE_INTERVAL_FRAMES = FPS // 2 # 30 frames para 500ms
wave_timer = 0 # Temporizador para la nueva lógica de olas
# ----------------------------------------

# Helper: Busca una instancia de AreaAbility por tipo
def get_area_ability(ability_type):
    for ability in area_abilities:
        if ability.ability_type == ability_type:
            return ability
    return None

while running:
    # 1. Entrada de Eventos
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if game_state == "running":
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
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


    # 2. Lógica de Juego
    if game_state == "running":
        
        # 2.1 Actualización de Sprites
        all_sprites.update()
        enemies.update()
        projectiles.update()
        bumerangs.update()
        ray_of_frosts.update()
        area_abilities.update()
        player.update()
        orbs.update()
        
        # 2.2 Generación de Enemigos (Lógica Exponencial)
        current_enemy_count = len(enemies)
        
        # Determinar el multiplicador de salud
        enemy_health_multiplier = 2.0 if current_enemy_count >= MAX_ENEMIES_LIMIT else 1.0

        wave_timer += 1
        
        if wave_timer >= WAVE_INTERVAL_FRAMES:
            wave_timer = 0
            
            # Calcular el número de enemigos a generar: 2^Nivel
            enemies_to_spawn = 2 ** player.level
            
            # Limitar la cantidad total de enemigos
            max_spawnable = MAX_ENEMIES_LIMIT - current_enemy_count
            num_to_spawn = max(0, min(enemies_to_spawn, max_spawnable)) # Asegura que no sea negativo

            for _ in range(num_to_spawn):
                # Lógica para determinar x e y (fuera de pantalla)
                if random.choice([True, False]): 
                    x = random.choice([0, SCREEN_WIDTH])
                    y = random.randint(0, SCREEN_HEIGHT)
                else:
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.choice([0, SCREEN_HEIGHT])
                    
                # Crear enemigo con el multiplicador de salud
                Enemy(x, y, player, (all_sprites, enemies), health_multiplier=enemy_health_multiplier)
            
        # 2.3 Generación de ataques por el jugador
        attack_data = player.get_attack_data()
        
        # Dirección base (enemigo más cercano o aleatoria)
        base_direction = pygame.math.Vector2(random.uniform(-1, 1), random.uniform(-1, 1)).normalize()
        if enemies:
            closest_enemy = min(enemies, key=lambda e: player.pos.distance_to(e.pos))
            base_direction = pygame.math.Vector2(closest_enemy.rect.center) - player.pos
            if base_direction.length_squared() > 0:
                base_direction = base_direction.normalize()


        if attack_data:
            
            if attack_data["type"] == "Daga Rápida":
                 for _ in range(attack_data["count"]):
                    random_angle = random.uniform(0, 2 * math.pi)
                    random_direction = pygame.math.Vector2(math.cos(random_angle), math.sin(random_angle))
                    Projectile(player.rect.centerx, player.rect.centery, random_direction, attack_data["damage"], (all_sprites, projectiles))

            elif attack_data["type"] == "Rayo de Escarcha":
                RayOfFrost(player.rect.centerx, player.rect.centery, base_direction, attack_data["damage"], (all_sprites, ray_of_frosts))
                
            elif attack_data["type"] == "Bumerang":
                for _ in range(attack_data["count"]):
                     Bumerang(player, attack_data["damage"], attack_data["speed"], attack_data["lifetime"], (all_sprites, bumerangs))

            # Creación única del Aura de Fuego (Solo si no existe)
            elif attack_data["type"] == "Aura de Fuego":
                 if not get_area_ability("fire"):
                    AreaAbility(
                        player, 
                        attack_data["damage"], 
                        attack_data["radius"], 
                        attack_data["cooldown"], 
                        (all_sprites, area_abilities), 
                        ability_type="fire"
                    )

            # Creación única del Aura de Magnetismo (Solo si no existe)
            elif attack_data["type"] == "Aura de Magnetismo":
                 if not get_area_ability("magnetism"):
                    AreaAbility(
                        player, 
                        attack_data["damage"], 
                        attack_data["radius"], # Este es el multiplicador
                        attack_data["cooldown"], 
                        (all_sprites, area_abilities), 
                        ability_type="magnetism"
                    )


        # 2.4 Colisiones y Lógica de Daño de Fuego
        current_time = pygame.time.get_ticks()
        fire_aura = get_area_ability("fire")
        if fire_aura and current_time - last_fire_damage_time > fire_aura.cooldown:
            last_fire_damage_time = current_time
            
            for enemy in enemies:
                # Colisión usando el radio de daño real (damage_radius)
                if enemy.pos.distance_to(fire_aura.rect.center) < fire_aura.damage_radius: 
                    if enemy.take_damage(fire_aura.damage):
                        ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs))


        # Proyectiles, Rayo de Escarcha y Bumerán vs Enemigo
        hits = pygame.sprite.groupcollide(projectiles, enemies, True, False)
        for projectile, hit_enemies in hits.items():
            for enemy in hit_enemies:
                if enemy.take_damage(projectile.damage):
                    ExperienceOrb(enemy.rect.centerx, enemy.rect.centery, 1, (orbs))
        
        
        # 2.5 Lógica de Aura de Magnetismo (Radio de Recolección)
        magnet_aura = get_area_ability("magnetism")
        # El atributo 'radius_multiplier' se guarda en el Aura de Magnetismo
        magnet_radius_multiplier = magnet_aura.radius_multiplier if magnet_aura else 1.0 
        
        # Jugador vs Orbe y Actualización del radio de recolección
        for orb in orbs:
            # Pasa el multiplicador al orbe
            orb.set_target(player, magnetism_aura_radius=magnet_radius_multiplier) 

        orb_hits = pygame.sprite.spritecollide(player, orbs, True)
        for orb in orb_hits:
            if player.add_experience(orb.amount):
                # Solo cambiamos el estado si hay opciones de mejora disponibles (Evita mostrar el menú si todo está al máximo)
                if obtener_opciones_subida_nivel(player.active_abilities):
                    game_state = "level_up"
                    level_up_menu.activate()
            

    # 3. Dibujo
    
    # --- DIBUJO DEL FONDO (PRIMERO) ---
    if BACKGROUND_IMAGE:
        screen.blit(BACKGROUND_IMAGE, (0, 0))
    else:
        screen.fill(BLACK) 
    # -----------------------------------
    
    # 1. Dibujar Auras con el método custom DEBAJO del jugador
    for ability in area_abilities:
        # CORRECCIÓN: Usa draw_custom para evitar el AttributeError
        ability.draw_custom(screen) 
    
    # 2. Dibujar Proyectiles, Orbes y Enemigos
    enemies.draw(screen)
    projectiles.draw(screen)
    bumerangs.draw(screen)
    ray_of_frosts.draw(screen)
    orbs.draw(screen)
    
    # Dibujar barras de vida de enemigos
    if game_state == "running":
        for enemy in enemies:
            enemy.draw_health_bar(screen)

    # 3. Dibujar el JUGADOR AL FINAL
    screen.blit(player.image, player.rect) 
    
    # Dibujar HUD (Interfaz de usuario)
    font = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 30)

    # --- HUD Principal ---
    y_hud_offset = 10
    text = font.render(f"Nivel: {player.level} | EXP: {player.experience}", True, WHITE)
    screen.blit(text, (10, y_hud_offset))
    y_hud_offset += 30
    text = font.render(f"HP: {player.health}/{player.max_health}", True, RED)
    screen.blit(text, (10, y_hud_offset))
    
    # Contador de Enemigos (Arriba a la derecha)
    difficulty_text = ""
    if enemy_health_multiplier > 1.0:
        difficulty_text = f" | Dificultad: x{int(enemy_health_multiplier)}"
    
    enemy_count_text = font.render(f"ENEMIGOS: {current_enemy_count}/{MAX_ENEMIES_LIMIT}{difficulty_text}", True, WHITE)
    screen.blit(enemy_count_text, (SCREEN_WIDTH - enemy_count_text.get_width() - 10, 10))

    # Habilidades Activas (Abajo a la izquierda)
    abilities_title = font.render("HABILIDADES ACTIVAS:", True, WHITE)
    screen.blit(abilities_title, (10, SCREEN_HEIGHT - 130)) 
    y_abil_offset = SCREEN_HEIGHT - 100 
    
    for hid, level in player.active_abilities.items():
        if hid in HABILIDADES_MAESTRAS:
            name = HABILIDADES_MAESTRAS[hid]["nombre"]
            ability_text = font_small.render(f"- {name} (Nv. {level})", True, WHITE)
            screen.blit(ability_text, (20, y_abil_offset))
            y_abil_offset += 25


    # Dibujar Menús (si están activos)
    if game_state == "level_up":
        level_up_menu.draw(screen)
    elif game_state == "paused":
        pause_menu.draw(screen)
        
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()