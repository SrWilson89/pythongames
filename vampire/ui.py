# ui.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, BLACK, WHITE, GREEN, RED, BLUE
from abilities import HABILIDADES_MAESTRAS, describir_opcion, obtener_opciones_subida_nivel

# --- CLASE: MENU DE SUBIDA DE NIVEL ---

class LevelUpMenu:
    def __init__(self, player):
        self.player = player
        self.is_active = False
        self.font_title = pygame.font.Font(None, 60)
        self.font_option = pygame.font.Font(None, 40)
        self.options = [] # Lista de tuplas (id, tipo)
        self.current_selection = 0
        
        # Definición del área del menú
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 4, 
            SCREEN_HEIGHT // 4, 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2
        )

    def activate(self):
        self.is_active = True
        self.current_selection = 0
        # OBTENER OPCIONES REALES
        self.options = obtener_opciones_subida_nivel(self.player.active_abilities)

    def deactivate(self):
        self.is_active = False
        
    def handle_input(self, event):
        """Maneja la navegación, selección y aplicación de mejoras."""
        if not self.is_active:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                # Aplicar la mejora y cerrar el menú
                chosen_option = self.options[self.current_selection]
                self.player.apply_ability_choice(chosen_option)
                return "closed"
                
        return None

    def draw(self, surface):
        if not self.is_active:
            return

        # Capa semi-transparente
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) # Más oscuro para que se note
        surface.blit(overlay, (0, 0))

        # Marco del menú
        pygame.draw.rect(surface, BLACK, self.rect, 0)
        pygame.draw.rect(surface, WHITE, self.rect, 5)

        y_offset = self.rect.top + 40
        title_text = self.font_title.render("¡SUBIDA DE NIVEL!", True, GREEN)
        surface.blit(title_text, (self.rect.centerx - title_text.get_width() // 2, y_offset))
        y_offset += 80
        
        # Dibujar opciones
        for i, option in enumerate(self.options):
            # PASAR active_abilities a describir_opcion
            text_line = describir_opcion(option, self.player.active_abilities) 
            
            color = GREEN if i == self.current_selection else WHITE
            
            # Dibujar el rectángulo de selección
            option_rect = pygame.Rect(self.rect.left + 20, y_offset, self.rect.width - 40, 60)
            if i == self.current_selection:
                pygame.draw.rect(surface, BLUE, option_rect, 0) # Fondo azul
            pygame.draw.rect(surface, color, option_rect, 2) # Borde

            text_surface = self.font_option.render(text_line, True, color)
            surface.blit(text_surface, (option_rect.left + 10, option_rect.top + 15))
            
            y_offset += 80
            
# --- CLASE: MENU DE PAUSA ---

class PauseMenu:
    def __init__(self):
        self.is_active = False
        self.font = pygame.font.Font(None, 60)
        self.options = ["Reanudar", "Silenciar/Activar Sonido", "Salir del Juego"]
        self.current_selection = 0
        
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 4, 
            SCREEN_HEIGHT // 4, 
            SCREEN_WIDTH // 2, 
            SCREEN_HEIGHT // 2
        )

    def activate(self):
        self.is_active = True
        self.current_selection = 0
        
    def deactivate(self):
        self.is_active = False
        
    def handle_input(self, event):
        if not self.is_active:
            return None
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                return "resume"
            elif event.key == pygame.K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.options)
            elif event.key == pygame.K_RETURN:
                
                if self.current_selection == 0:
                    return "resume"
                    
                elif self.current_selection == 1:
                    # Lógica de Silenciar/Activar Sonido (Asume que hay música)
                    if pygame.mixer.music.get_volume() > 0:
                        pygame.mixer.music.set_volume(0.0) 
                        # También silencia canales de sonido (si existieran)
                        for sound_id in range(pygame.mixer.get_num_channels()):
                            pygame.mixer.Channel(sound_id).set_volume(0.0)
                    else:
                        pygame.mixer.music.set_volume(1.0) 
                        for sound_id in range(pygame.mixer.get_num_channels()):
                            pygame.mixer.Channel(sound_id).set_volume(1.0)
                            
                elif self.current_selection == 2:
                    return "quit"   
                
        return None

    def draw(self, surface):
        if not self.is_active:
            return

        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 150)) 
        surface.blit(overlay, (0, 0))

        pygame.draw.rect(surface, BLACK, self.rect, 0)
        pygame.draw.rect(surface, WHITE, self.rect, 5)

        y_offset = self.rect.top + 40
        title_text = self.font.render("JUEGO EN PAUSA", True, WHITE)
        surface.blit(title_text, (self.rect.centerx - title_text.get_width() // 2, y_offset))
        y_offset += 80
        
        for i, text_base in enumerate(self.options):
            color = GREEN if i == self.current_selection else WHITE
            text = text_base
            
            option_rect = pygame.Rect(self.rect.left + 40, y_offset, self.rect.width - 80, 50)
            if i == self.current_selection:
                pygame.draw.rect(surface, RED, option_rect, 0)
                
            text_surface = self.font.render(text, True, color)
            surface.blit(text_surface, (self.rect.centerx - text_surface.get_width() // 2, y_offset + 5))
            
            y_offset += 60