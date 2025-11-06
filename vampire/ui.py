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
        # ¡CORRECCIÓN CLAVE 1: OBTENER OPCIONES REALES!
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
                if self.options:
                    chosen_option = self.options[self.current_selection]
                    self.player.apply_ability_choice(chosen_option)
                    self.deactivate()
                    return "chosen"
                
        return None
        
    def draw(self, surface):
        """Dibuja el menú de subida de nivel sobre el juego."""
        if not self.is_active:
            return
            
        # Dibuja un fondo semi-transparente
        overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180)) 
        surface.blit(overlay, (0, 0))
        
        # Dibuja el marco del menú
        pygame.draw.rect(surface, BLACK, self.rect, 0)
        pygame.draw.rect(surface, WHITE, self.rect, 5)

        # Título
        title_text = self.font_title.render("¡SUBIDA DE NIVEL!", True, GREEN)
        surface.blit(title_text, (self.rect.centerx - title_text.get_width() // 2, self.rect.top + 30))
        
        y_offset = self.rect.top + 120
        
        # Opciones
        for i, option in enumerate(self.options):
            text_line = describir_opcion(option)
            
            color = WHITE
            # Resaltar la opción seleccionada
            if i == self.current_selection:
                color = GREEN
                pygame.draw.rect(surface, (50, 50, 50), (self.rect.left + 20, y_offset - 5, self.rect.width - 40, 50), 0)

            option_text = self.font_option.render(text_line, True, color)
            surface.blit(option_text, (self.rect.left + 50, y_offset))
            y_offset += 60

# --- CLASE: MENU DE PAUSA (Se mantiene igual, solo se actualiza la fuente) ---

class PauseMenu:
    def __init__(self, surface):
        self.surface = surface
        self.is_active = False
        self.font = pygame.font.Font(None, 48)
        self.options = ["Reanudar", "Ajustes de Sonido", "Salir del Juego"]
        self.current_selection = 0
        
        self.rect = pygame.Rect(
            SCREEN_WIDTH // 3, 
            SCREEN_HEIGHT // 4, 
            SCREEN_WIDTH // 3, 
            SCREEN_HEIGHT // 2
        )
        
        if not pygame.mixer.get_init():
             pygame.mixer.init() 
        self.is_muted = False

    def activate(self):
        self.is_active = True
        self.current_selection = 0

    def deactivate(self):
        self.is_active = False

    def handle_input(self, event):
        if not self.is_active:
            return None

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.current_selection = (self.current_selection - 1) % len(self.options)
            elif event.key == pygame.K_DOWN:
                self.current_selection = (self.current_selection + 1) % len(self.options)
                
            elif event.key == pygame.K_RETURN:
                if self.current_selection == 0:
                    return "unpause" 
                elif self.current_selection == 1:
                    self.is_muted = not self.is_muted
                    if self.is_muted:
                        pygame.mixer.music.set_volume(0.0)
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
            
            if i == 1:
                text = f"Ajustes de Sonido: {'MUTEADO' if self.is_muted else 'ACTIVO'}"

            option_text = self.font.render(text, True, color)
            surface.blit(option_text, (self.rect.left + 50, y_offset))
            y_offset += 60