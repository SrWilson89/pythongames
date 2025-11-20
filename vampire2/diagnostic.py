# diagnostic.py - ¡CORREGIDO!
import pygame
import os
import sys

# =======================================================
# FUNCIÓN DE RUTA ROBUSTA
# =======================================================
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)
# =======================================================


def run_diagnostic():
    print("--- INICIANDO DIAGNÓSTICO DE ASSETS Y PYGAME ---")

    try:
        pygame.init()
        print("✅ Pygame inicializado correctamente.")
    except Exception as e:
        print(f"❌ ERROR: Pygame no pudo inicializarse. ({e})")
        return
        
    # SOLUCIÓN: Crear una pantalla mínima para permitir la conversión de imágenes
    try:
        screen = pygame.display.set_mode((1, 1), pygame.HIDDEN)
        print("✅ Modo de video temporal (1x1) establecido.")
    except Exception as e:
        print(f"❌ ERROR: No se pudo establecer el modo de video. ({e})")
        pygame.quit()
        return


    # 2. Chequeo de Ruta de Assets
    asset_folder = resource_path("assets/sprites")
    if os.path.isdir(asset_folder):
        print(f"✅ Carpeta de assets encontrada: {asset_folder}")
    else:
        print(f"❌ ERROR: Carpeta de assets NO encontrada en: {asset_folder}")
        print("   VERIFICA tu comando PyInstaller: --add-data 'assets;assets'")
        pygame.quit()
        return

    # 3. Chequeo de Carga de Sprite (Jugador)
    sprite_path = resource_path("assets/sprites/player.png")
    if not os.path.exists(sprite_path):
        print(f"❌ ERROR: Sprite 'player.png' NO encontrado en: {sprite_path}")
        print("   Asegúrate de que 'player.png' esté en assets/sprites.")
        pygame.quit()
        return

    try:
        # La carga y conversión ahora funcionará gracias al set_mode()
        image = pygame.image.load(sprite_path).convert_alpha()
        print(f"✅ Sprite 'player.png' cargado correctamente. Tamaño: {image.get_size()}")
    except pygame.error as e:
        print(f"❌ ERROR: No se pudo cargar 'player.png', aunque la ruta existe. ({e})")
        print("   Esto suele ser un problema de un archivo de imagen corrupto.")
        pygame.quit()
        return

    # 4. Chequeo de Carga de Fondo
    background_path = resource_path("assets/background/tile.png")
    if not os.path.exists(background_path):
        print(f"❌ ERROR: Fondo 'tile.png' NO encontrado en: {background_path}")
        print("   Asegúrate de que 'tile.png' esté en assets/background.")
        pygame.quit()
        return

    try:
        pygame.image.load(background_path).convert()
        print("✅ Fondo 'tile.png' cargado correctamente.")
    except pygame.error as e:
        print(f"❌ ERROR: No se pudo cargar 'tile.png'. ({e})")
        pygame.quit()
        return

    # 5. Todo OK
    print("\n🎉 ¡DIAGNÓSTICO COMPLETO Y EXITOSO! El problema es de visibilidad (offset) en main.py.")
    pygame.quit()

if __name__ == "__main__":
    run_diagnostic()