# ui.py - VERSIÓN COMPLETA CON RATÓN + TECLADO
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
        self.options = []
        self.current_selection = 0
        self.option_rects = []

    def apply_selection(self, index):
        if 0 <= index < len(self.options):
            hid, tipo = self.options[index]
            if tipo == "Nueva":
                self.player.add_new_ability(hid)
            elif tipo == "Mejora":
                self.player.upgrade_ability(hid)
            self.deactivate()
            return "closed"
        return None

    def handle_input(self, event):
        if not self.active:
            return None

        num_options = len(self.options)

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.current_selection = (self.current_selection - 1) % num_options
            elif event.key == pygame.K_DOWN:
                self.current_selection = (self.current_selection + 1) % num_options
            elif event.key == pygame.K_RETURN:
                return self.apply_selection(self.current_selection)
            elif event.key in (pygame.K_1, pygame.K_2, pygame.K_3):
                index = event.key - pygame.K_1
                if index < num_options:
                    return self.apply_selection(index)

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:  # Click izquierdo
                mouse_pos = event.pos
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(mouse_pos):
                        return self.apply_selection(i)

        return None

    def draw(self, surface):
        if not self.active:
            return

        # Overlay transparente
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150))
        surface.blit(overlay, (0, 0))

        # Fondo del menú
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        # Título
        title_text = self.font_title.render("¡SUBIDA DE NIVEL!", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.rect.centerx)
        surface.blit(title_text, (title_rect.x, self.rect.y + self.padding))

        # Instrucciones
        y_offset = self.rect.y + 70
        instr_text = self.font_option.render("↑↓ Flechas/Click | ENTER/1-3 para seleccionar", True, WHITE)
        surface.blit(instr_text, (self.rect.x + self.padding, y_offset))
        y_offset += 50

        # Opciones (con rects para ratón)
        self.option_rects = []
        for i, option in enumerate(self.options):
            hid, tipo = option
            text_line = describir_opcion(hid, tipo, self.player.active_abilities)

            option_rect = pygame.Rect(self.rect.x + self.padding, y_offset, 
                                    self.width - 2 * self.padding, 80)
            self.option_rects.append(option_rect)

            # Colores
            color_base = [(50, 50, 150), (50, 150, 50), (150, 50, 50)][i]
            if i == self.current_selection:
                color = tuple(min(255, c + 50) for c in color_base)
                pygame.draw.rect(surface, color, option_rect, border_radius=10)
                pygame.draw.rect(surface, (255, 255, 0), option_rect, 4, border_radius=10)
            else:
                pygame.draw.rect(surface, color_base, option_rect, border_radius=10)
                pygame.draw.rect(surface, WHITE, option_rect, 2, border_radius=10)

            # Número
            num_text = self.font_option.render(f"[{i+1}]", True, WHITE)
            surface.blit(num_text, (option_rect.x + 10, option_rect.y + 10))

            # Descripción
            desc_text = self.font_option.render(text_line, True, WHITE)
            surface.blit(desc_text, (option_rect.x + 60, option_rect.y + 10))

            y_offset += 90

# --- CLASE: MENU DE PAUSA (RATÓN + TECLADO) ---
class PauseMenu:
    def __init__(self):
        self.active = False
        self.font = pygame.font.Font(None, 60)
        self.font_option = pygame.font.Font(None, 40)
        self.options = ["Reanudar [ESC]", "Salir al escritorio"]
        
        self.width = 400
        self.height = 300
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) / 2, 
            (SCREEN_HEIGHT - self.height) / 2, 
            self.width, 
            self.height
        )
        self.padding = 30
        self.button_rects = []

    def activate(self):
        self.active = True

    def handle_input(self, event):
        if not self.active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.active = False
                return "resume"
            elif event.key == pygame.K_q:  # Q para salir
                return "quit"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                mouse_pos = event.pos
                # Botón Salir
                if self.button_rects and self.button_rects[1].collidepoint(mouse_pos):
                    return "quit"

        return None

    def draw(self, surface):
        if not self.active:
            return

        # Overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        # Título
        title_text = self.font.render("JUEGO PAUSADO", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.rect.centerx)
        surface.blit(title_text, (title_rect.x, self.rect.y + self.padding))

        y_offset = self.rect.y + 100
        self.button_rects = []

        # Opción 1: Reanudar
        resume_text = self.font_option.render(self.options[0], True, WHITE)
        surface.blit(resume_text, (self.rect.x + self.padding, y_offset))
        y_offset += 70

        # Opción 2: Salir (botón clickable)
        quit_rect = pygame.Rect(self.rect.x + self.padding, y_offset, 
                              self.width - 2 * self.padding, 60)
        self.button_rects = [None, quit_rect]  # [0]=None, [1]=quit
        
        pygame.draw.rect(surface, RED, quit_rect, border_radius=10)
        pygame.draw.rect(surface, WHITE, quit_rect, 2, border_radius=10)
        
        quit_text = self.font_option.render(self.options[1], True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        surface.blit(quit_text, quit_text_rect)