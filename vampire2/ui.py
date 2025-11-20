# ui.py - CLASES DE UI
import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, WHITE, BLACK, RED, GREEN, BLUE
from abilities import obtener_opciones_subida_nivel, describir_opcion
# Necesitas la función resource_path aquí si LevelUpMenu usa imágenes.
# Si no usa imágenes, solo necesitas las clases.

# =======================================================
# CLASE: MENU DE SUBIDA DE NIVEL 
# (Asumo que esta ya funcionaba)
# =======================================================
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
        self.option_rects = []

    def activate(self):
        self.active = True
        self.options = obtener_opciones_subida_nivel(self.player.active_abilities)
        self.current_selection = 0
        self.option_rects = []
        
    def handle_input(self, key):
        if key == pygame.K_UP:
            self.current_selection = max(0, self.current_selection - 1)
        elif key == pygame.K_DOWN:
            self.current_selection = min(len(self.options) - 1, self.current_selection + 1)
        elif key == pygame.K_RETURN:
            if self.options:
                return self.options[self.current_selection]["id"], self.options[self.current_selection]["tipo"]
        return None

    def handle_mouse_click(self, mouse_pos):
        if not self.active: return None
        for i, rect in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                return self.options[i]["id"], self.options[i]["tipo"]
        return None

    def draw(self, surface):
        if not self.active: return

        # ... (Lógica de dibujo de LevelUpMenu) ...
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        title_text = self.font_title.render("¡SUBES DE NIVEL!", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.rect.centerx)
        surface.blit(title_text, (title_rect.x, self.rect.y + self.padding))

        y_offset = self.rect.y + 80
        self.option_rects = []

        for i, option in enumerate(self.options):
            # Dibujar rectángulo de opción
            option_rect = pygame.Rect(self.rect.x + self.padding, y_offset, self.width - 2 * self.padding, 80)
            self.option_rects.append(option_rect)

            # Resaltar la seleccionada
            color = BLUE if i == self.current_selection else BLACK
            pygame.draw.rect(surface, color, option_rect)
            pygame.draw.rect(surface, WHITE, option_rect, 2)

            # Dibujar texto
            tipo = option["tipo"]
            desc_text = describir_opcion(option["id"], self.player.active_abilities.get(option["id"], 0), tipo)
            
            title = self.font_option.render(f"[{tipo}] {desc_text.split('.')[0]}", True, WHITE)
            surface.blit(title, (option_rect.x + 10, option_rect.y + 10))
            
            description = self.font_option.render(desc_text.split('.', 1)[-1].strip(), True, WHITE)
            surface.blit(description, (option_rect.x + 10, option_rect.y + 45))
            
            y_offset += 90


# =======================================================
# CLASE: MENU DE PAUSA (CORREGIDO)
# =======================================================
class PauseMenu:
    def __init__(self):
        self.font = pygame.font.Font(None, 60)
        self.font_option = pygame.font.Font(None, 36)
        
        # Configuración de la UI
        self.width = SCREEN_WIDTH * 0.4
        self.height = SCREEN_HEIGHT * 0.4
        self.rect = pygame.Rect(
            (SCREEN_WIDTH - self.width) / 2, 
            (SCREEN_HEIGHT - self.height) / 2, 
            self.width, 
            self.height
        )
        self.padding = 30
        self.options = ["Reanudar (R)", "Salir (Q)"]
        self.button_rects = []
        
    def handle_input(self, key): # <--- MÉTODO AÑADIDO PARA SOLUCIONAR EL ATTRIBUTEERROR
        """Maneja el input del teclado (R para Reanudar, Q para Salir)."""
        if key == pygame.K_r:
            return "resume"
        if key == pygame.K_q:
            return "quit"
        return None

    def handle_mouse_click(self, mouse_pos):
        # Lógica de clic de ratón (Si la tenías implementada)
        if not self.button_rects: return None
        if self.button_rects[0].collidepoint(mouse_pos):
            return "resume"
        if self.button_rects[1].collidepoint(mouse_pos):
            return "quit"
        return None

    def draw(self, surface):
        # Overlay
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        surface.blit(overlay, (0, 0))

        # Cuadro principal
        pygame.draw.rect(surface, BLACK, self.rect)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        # Título
        title_text = self.font.render("JUEGO PAUSADO", True, WHITE)
        title_rect = title_text.get_rect(centerx=self.rect.centerx)
        surface.blit(title_text, (title_rect.x, self.rect.y + self.padding))

        # Opciones
        y_offset = self.rect.y + 100
        self.button_rects = []

        # Opción 1: Reanudar
        resume_rect = pygame.Rect(self.rect.x + self.padding, y_offset, self.width - 2 * self.padding, 60)
        self.button_rects.append(resume_rect)
        pygame.draw.rect(surface, (50, 50, 50), resume_rect)
        pygame.draw.rect(surface, WHITE, resume_rect, 2)
        resume_text = self.font_option.render(self.options[0], True, WHITE)
        resume_text_rect = resume_text.get_rect(center=resume_rect.center)
        surface.blit(resume_text, resume_text_rect)
        y_offset += 70

        # Opción 2: Salir
        quit_rect = pygame.Rect(self.rect.x + self.padding, y_offset, self.width - 2 * self.padding, 60)
        self.button_rects.append(quit_rect)
        pygame.draw.rect(surface, (50, 50, 50), quit_rect)
        pygame.draw.rect(surface, WHITE, quit_rect, 2)
        quit_text = self.font_option.render(self.options[1], True, WHITE)
        quit_text_rect = quit_text.get_rect(center=quit_rect.center)
        surface.blit(quit_text, quit_text_rect)