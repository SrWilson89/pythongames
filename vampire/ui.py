# ui.py

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN
from abilities import HABILIDADES_MAESTRAS, obtener_opciones_subida_nivel

class LevelUpMenu:
    def __init__(self, player):
        self.player = player
        self.is_active = False
        self.options = []
        self.font = pygame.font.Font(None, 36) 
        self.current_selection = 0
        
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 4, 
            SCREEN_HEIGHT // 4, 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2
        )

    def activate(self):
        """Prepara y muestra el menú."""
        self.is_active = True
        self.current_selection = 0
        self.generate_options()

    def deactivate(self):
        self.is_active = False

    def generate_options(self):
        """Genera las 3 opciones de habilidad."""
        self.options = obtener_opciones_subida_nivel(self.player.active_abilities)
        self.options.append(("Skip", "Skip"))

    def handle_input(self, event):
        """Maneja la selección del jugador."""
        if not self.is_active:
            return False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.current_selection = max(0, self.current_selection - 1)
            elif event.key == pygame.K_DOWN:
                self.current_selection = min(len(self.options) - 1, self.current_selection + 1)
                
            elif event.key == pygame.K_RETURN:
                return self._select_option()

        return False

    def _select_option(self):
        """Procesa la opción elegida."""
        opcion_elegida = self.options[self.current_selection]
        id_elegida, tipo_elegido = opcion_elegida
        
        if tipo_elegido == "Skip":
            if self.player.skips_restantes > 0:
                self.player.skips_restantes -= 1
                self.generate_options() 
            else:
                print("No quedan skips gratis.")
            return True 
        
        else: 
            nivel_actual = self.player.active_abilities.get(id_elegida, 0)
            
            # Si el Aura de Fuego (ID 3) acaba de ser seleccionada, la creamos
            if id_elegida == 3 and nivel_actual == 0:
                # Retorna un valor especial que main.py usará para crear el sprite del aura
                self.player.active_abilities[id_elegida] = nivel_actual + 1
                self.deactivate()
                return "AuraCreated" 
            
            self.player.active_abilities[id_elegida] = nivel_actual + 1
            self.deactivate()
            return False 
            
    def draw(self, surface):
        """Dibuja el menú de selección."""
        if not self.is_active:
            return

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, BLACK, self.rect, 0)
        pygame.draw.rect(surface, WHITE, self.rect, 3)

        y_offset = self.rect.top + 20
        title_text = self.font.render("¡SUBIDA DE NIVEL!", True, WHITE)
        surface.blit(title_text, (self.rect.centerx - title_text.get_width() // 2, y_offset))
        y_offset += 50
        
        for i, (id_habilidad, tipo) in enumerate(self.options):
            
            color = GREEN if i == self.current_selection else WHITE
            
            if tipo == "Skip":
                text = f"[S] Saltar (Skips: {self.player.skips_restantes})"
                
            else:
                nombre = HABILIDADES_MAESTRAS[id_habilidad]["nombre"]
                max_nivel = HABILIDADES_MAESTRAS[id_habilidad]["max_nivel"]
                nivel_actual = self.player.active_abilities.get(id_habilidad, 0)
                
                if tipo == "Mejora":
                    info = f"Mejorar a Nivel {nivel_actual + 1}/{max_nivel}"
                else:
                    info = f"Obtener (Nivel 1/{max_nivel})"
                    
                text = f"[{i+1}] {nombre} - {info}"

            option_text = self.font.render(text, True, color)
            surface.blit(option_text, (self.rect.left + 20, y_offset))
            y_offset += 40
            
        if self.current_selection < len(self.options) - 1:
            pointer = self.font.render(">", True, GREEN)
            surface.blit(pointer, (self.rect.left, self.rect.top + 50 + self.current_selection * 40))