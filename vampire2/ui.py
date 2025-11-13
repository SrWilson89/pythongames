# ui.py - VERSIÓN COMPLETA CON RATÓN + TECLADO Y DEACTIVATE
# (Reemplaza todo el archivo ui.py con esto)

import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE
from abilities import obtener_opciones_subida_nivel, describir_opcion

# --- CLASE: MENU DE SUBIDA DE NIVEL (RATÓN + TECLADO) ---
class LevelUpMenu:
    def __init__(self, player):
        self.player = player
        self.active = False
        self.options = []
        self.current_selection = 0

        # Configuración de la UI
        self.font_title = pygame.font.Font(None, 60)
        self.font_option = pygame.font.Font(None, 36)
        self.width = SCREEN_WIDTH * 0.7
        self.height = SCREEN_HEIGHT * 0.7
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) / 2, 
            (SCREEN_HEIGHT - self.height) / 2, 
            self.width, 
            self.height
        )
        self.padding = 20
        self.option_rects = []  # Rects para clics del ratón

    def activate(self):
        self.active = True
        self.options = obtener_opciones_subida_nivel(self.player.active_abilities)
        self.current_selection = 0
        
    def deactivate(self):
        self.active = False

    def handle_keyboard(self, key):
        if not self.active:
            return None

        if key == pygame.K_UP:
            self.current_selection = (self.current_selection - 1) % len(self.options)
        elif key == pygame.K_DOWN:
            self.current_selection = (self.current_selection + 1) % len(self.options)
        elif key == pygame.K_RETURN:
            # Opción seleccionada
            return self.options[self.current_selection][0] # Devuelve el ID de la habilidad

        return None

    def handle_click(self, mouse_pos):
        if not self.active:
            return None
        
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                return self.options[i][0] # Devuelve el ID de la habilidad
        return None

    def draw(self, surface):
        if not self.active:
            return

        # Overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Marco del menú
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        # Título
        title_text = self.font_title.render("¡SUBIDA DE NIVEL!", True, GREEN)
        title_rect = title_text.get_rect(centerx=self.rect.centerx)
        surface.blit(title_text, (title_rect.x, self.rect.y + self.padding))

        self.option_rects = []
        y_offset = self.rect.y + 100
        
        for i, (hid, tipo) in enumerate(self.options):
            # Obtener el texto de la opción
            display_text = describir_opcion(hid, tipo, self.player)
            
            # Dibujar el marco de la opción
            option_rect = pygame.Rect(
                self.rect.x + self.padding, 
                y_offset, 
                self.width - 2 * self.padding, 
                70
            )
            self.option_rects.append(option_rect)
            
            # Resaltar la opción seleccionada (teclado)
            if i == self.current_selection:
                pygame.draw.rect(surface, (50, 50, 50), option_rect) # Fondo gris oscuro
                pygame.draw.rect(surface, RED, option_rect, 3) # Borde rojo
            else:
                 pygame.draw.rect(surface, (20, 20, 20), option_rect) # Fondo gris muy oscuro

            # Dibujar el texto
            lines = display_text.split('\n')
            
            # Línea 1 (Título de la opción)
            title_line = self.font_option.render(lines[0], True, WHITE)
            surface.blit(title_line, (option_rect.x + 10, option_rect.y + 5))
            
            # Línea 2 (Descripción)
            if len(lines) > 1:
                desc_line = self.font_option.render(lines[1], True, (150, 150, 150))
                surface.blit(desc_line, (option_rect.x + 10, option_rect.y + 35))
            
            y_offset += 80 # Espacio para la siguiente opción

# --- CLASE: MENU DE PAUSA ---
class PauseMenu:
    def __init__(self):
        self.active = False
        self.font = pygame.font.Font(None, 60)
        self.font_option = pygame.font.Font(None, 36)
        self.width = 400
        self.height = 300
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) / 2, 
            (SCREEN_HEIGHT - self.height) / 2, 
            self.width, 
            self.height
        )
        self.padding = 20
        self.options = ["REANUDAR", "SALIR"]
        self.button_rects = []
        
    def activate(self):
        self.active = True
        
    def deactivate(self): # <--- MÉTODO FALTANTE AÑADIDO
        self.active = False

    def handle_click(self, mouse_pos):
        if not self.active:
            return None
        
        # Opciones: Reanudar y Salir
        for i, rect in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos):
                if i == 0:
                    return "resume"
                elif i == 1:
                    return "quit"
        return None

    def draw(self, surface):
        if not self.active:
            return

        # Overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Marco del menú
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        # Título
        title_text = self.font.render("JUEGO PAUSADO", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.rect.centerx)
        surface.blit(title_text, (title_rect.x, self.rect.y + self.padding))

        y_offset = self.rect.y + 100
        self.button_rects = [] # Reiniciar los rects

        # Opción 1: Reanudar
        resume_rect = pygame.Rect(self.rect.x + self.padding, y_offset, 
                                 self.width - 2 * self.padding, 60)
        self.button_rects.append(resume_rect)
        pygame.draw.rect(surface, GREEN, resume_rect, 0, 5) 
        resume_text = self.font_option.render(self.options[0], True, BLACK)
        resume_text_rect = resume_text.get_rect(center=resume_rect.center)
        surface.blit(resume_text, resume_text_rect)
        y_offset += 80

        # Opción 2: Salir
        quit_rect = pygame.Rect(self.rect.x + self.padding, y_offset, 
                              self.width - 2 * self.padding, 60)
        self.button_rects.append(quit_rect)
        pygame.draw.rect(surface, RED, quit_rect, 0, 5)
        quit_text = self.font_option.render(self.options[1], True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        surface.blit(quit_text, quit_text_rect)