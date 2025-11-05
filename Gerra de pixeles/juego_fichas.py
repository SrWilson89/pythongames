import pygame
import random
from collections import deque
import time

# --- 1. CONSTANTES DE JUEGO MEJORADAS ESTÉTICAMENTE ---

# Dimensiones solicitadas: 1500x700
ANCHO_PANTALLA = 1500
ALTO_PANTALLA = 700

# Tamaño de celda: 20 de ancho
TAMANO_CELDA = 20
FILAS = ALTO_PANTALLA // TAMANO_CELDA
COLUMNAS = ANCHO_PANTALLA // TAMANO_CELDA

# --- PALETA DE COLORES MEJORADA ---
NEGRO_FONDO = (20, 20, 30)          # Fondo del menú y del HUD
GRIS_OSCURO_HUD = (30, 30, 45)      # Fondo del panel de información
VERDE_TABLERO = (0, 100, 0)         # Fondo del tablero de juego
BLANCO = (255, 255, 255)
NEGRO = (0, 0, 0)
AMARILLO_NEON = (255, 255, 0)
ROJO_ALERTA = (255, 60, 60)
AZUL_CLARO = (100, 100, 255) 
GRIS_CUADRICULA = (50, 50, 50)
COLOR_PERFECTA_INDICATOR = (255, 215, 0) # Dorado
COLOR_BOTON_NORMAL = (150, 150, 150)
COLOR_BOTON_SELECCION = (255, 100, 0)

# CONSTANTES DE UNIDAD PERFECTA
MAX_FICHAS_PERFECTAS = 500
EMOJI_OPTIONS = ["⭐", "👑", "🛡️", "⚔️", "🔥", "⚡", "🔮", "👽", "🦄", "🐉"]

# Paleta de 8 Colores BASE para Jugadores (Alto Contraste)
COLOR_PALETTE_BASE = [
    (200, 20, 20),     # 1. Rojo Intenso
    (20, 20, 200),     # 2. Azul Cobalto
    (0, 150, 0),       # 3. Verde Esmeralda
    (255, 120, 0),     # 4. Naranja Vibrante
    (150, 0, 150),     # 5. Púrpura Profundo
    (0, 150, 150),     # 6. Cian Turquesa
    (200, 200, 200),   # 7. Gris Claro
    (255, 255, 50)     # 8. Amarillo Brillante
]

# Configuración de juego (Se mantiene la funcionalidad)
BASE_TIEMPO_ENTRE_TURNOS = 1000  
MAX_MENSAJES = 5
LIMITE_TIEMPO_SEGUNDOS = 5 * 60 
PROBABILIDAD_COMBATE_BASE = 0.5 

# Ancho del Panel de la Interfaz
ANCHO_PANEL_DERECHO = 300 
ANCHO_TABLERO = ANCHO_PANTALLA - ANCHO_PANEL_DERECHO

# Funciones auxiliares para tonos de ficha
def aclarar_color(color, factor=0.7): 
    return tuple(min(255, int(c / factor)) for c in color)

def oscurecer_color(color, factor=0.7): 
    return tuple(max(0, int(c * factor)) for c in color)

COLOR_TONOS = {}
for i, base_color in enumerate(COLOR_PALETTE_BASE):
    COLOR_TONOS[base_color] = {
        "ligera": aclarar_color(base_color, 0.7), 
        "pesada": oscurecer_color(base_color, 0.7),
        "base": base_color
    }


# --- 2. INICIALIZACIÓN DE PYGAME Y FUENTES ---

pygame.init()
PANTALLA = pygame.display.set_mode((ANCHO_PANTALLA, ALTO_PANTALLA))
pygame.display.set_caption("Guerra de Píxeles Táctico")
RELOJ = pygame.time.Clock()

# FUENTES MEJORADAS (mayor tamaño, más impacto)
FUENTE_TITULO_GRANDE = pygame.font.SysFont('Consolas', 40, bold=True)
FUENTE_TITULO = pygame.font.SysFont('Consolas', 24, bold=True)
FUENTE_PRINCIPAL = pygame.font.SysFont('Consolas', 16)
FUENTE_CRONOMETRO = pygame.font.SysFont('Consolas', 36, bold=True)
FUENTE_GANADOR = pygame.font.SysFont('Consolas', 60, bold=True) 
FUENTE_ESTADISTICAS = pygame.font.SysFont('Consolas', 20, bold=True)
FUENTE_SMALL = pygame.font.SysFont('Consolas', 12)

# Fuente especial para emojis más pequeños
try:
    FUENTE_EMOJI = pygame.font.SysFont('Segoe UI Symbol', 18) 
except:
    FUENTE_EMOJI = pygame.font.SysFont('Arial', 18) 


# --- 3. CLASES FICHA, BUTTON Y DROPDOWN ---

class Button:
    def __init__(self, x, y, width, height, text, color_base, action=None, is_toggle=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color_base = color_base 
        self.action = action
        self.font = FUENTE_PRINCIPAL
        self.is_toggle = is_toggle 

    def draw(self, surface, is_selected=False):
        # Efecto de color al pasar el ratón
        mouse_pos = pygame.mouse.get_pos()
        is_hovered = self.rect.collidepoint(mouse_pos)
        
        button_color = self.color_base
        if is_selected:
            button_color = COLOR_BOTON_SELECCION 
        elif is_hovered:
            button_color = aclarar_color(self.color_base, 0.9)

        # Dibujar botón
        pygame.draw.rect(surface, button_color, self.rect, border_radius=5)
        
        # Borde para selección/hover
        if is_selected or is_hovered:
            pygame.draw.rect(surface, AMARILLO_NEON, self.rect, 2, border_radius=5)
            
        # Color de texto (Contraste)
        text_color = NEGRO if sum(button_color) > 380 else BLANCO
        text_surf = self.font.render(self.text, True, text_color)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def is_clicked(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class Dropdown:
    def __init__(self, x, y, w, h, main_text, options, font_label, font_option):
        self.main_rect = pygame.Rect(x, y, w, h)
        self.main_text = main_text
        self.options = options
        self.font_label = font_label
        self.font_option = font_option
        self.selected_option = options[0]
        self.is_open = False
        self.option_rects = []
        self.h = h
        self.color_main = GRIS_OSCURO_HUD
        self.color_open = (50, 50, 70)

    def draw(self, surface):
        # Dibujar botón principal
        pygame.draw.rect(surface, self.color_main, self.main_rect, border_radius=5)
        pygame.draw.rect(surface, AMARILLO_NEON, self.main_rect, 2, border_radius=5)
        
        # Texto de la etiqueta
        label_surf = self.font_label.render(f"{self.main_text}:", True, BLANCO)
        surface.blit(label_surf, (self.main_rect.x + 5, self.main_rect.y + 5))
        
        # Emoji seleccionado
        emoji_surf = self.font_option.render(self.selected_option, True, COLOR_PERFECTA_INDICATOR)
        emoji_rect = emoji_surf.get_rect(midright=(self.main_rect.right - 10, self.main_rect.centery))
        surface.blit(emoji_surf, emoji_rect)

        # Dibujar opciones si está abierto
        if self.is_open:
            self.option_rects = []
            # Crear una superficie que flote sobre el resto para el dropdown
            max_height = len(self.options) * self.h
            dropdown_surf = pygame.Surface((self.main_rect.width, max_height))
            dropdown_surf.fill(self.color_open)
            
            for i, option in enumerate(self.options):
                option_rect_local = pygame.Rect(0, self.h * i, self.main_rect.width, self.h)
                
                # Almacenar rects en coordenadas de pantalla
                option_rect_global = pygame.Rect(self.main_rect.x, self.main_rect.y + self.h * (i + 1), self.main_rect.width, self.h)
                self.option_rects.append(option_rect_global)
                
                color = AMARILLO_NEON if option == self.selected_option else self.color_open
                pygame.draw.rect(dropdown_surf, color, option_rect_local, 1)
                
                text_surf = self.font_option.render(option, True, BLANCO)
                text_rect = text_surf.get_rect(center=option_rect_local.center)
                dropdown_surf.blit(text_surf, text_rect)
                
            # Dibujar la superficie flotante
            surface.blit(dropdown_surf, (self.main_rect.x, self.main_rect.y + self.h))

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.main_rect.collidepoint(event.pos):
                self.is_open = not self.is_open
                return True
            
            if self.is_open:
                for i, rect in enumerate(self.option_rects):
                    if rect.collidepoint(event.pos):
                        self.selected_option = self.options[i]
                        self.is_open = False
                        return True
        return False

class Ficha:
    def __init__(self, color_base, fila, columna, tipo="ligera"):
        self.color_base = color_base 
        self.fila = fila
        self.columna = columna
        self.ha_actuado = False
        self.realizo_accion = False 
        self.tipo = tipo 
        self.es_actuando = False
        self.turnos_inactivos = 0
        
        if self.tipo == "pesada": 
            self.dados_combate = 5 
            self.puede_mover = False 
        elif self.tipo == "ligera": 
            self.dados_combate = 3 
            self.puede_mover = True
        else: # PERFECTA
            self.dados_combate = 5 
            self.puede_mover = True 
            
    def dibujar(self, pantalla):
        centro_x = self.columna * TAMANO_CELDA + TAMANO_CELDA // 2
        centro_y = self.fila * TAMANO_CELDA + TAMANO_CELDA // 2
        radio = TAMANO_CELDA // 2 - 2 
        
        if self.tipo in COLOR_TONOS[self.color_base]:
            color_real = COLOR_TONOS[self.color_base][self.tipo]
        else:
            color_real = oscurecer_color(self.color_base, 0.5) 

        # 1. Dibujar el círculo principal
        pygame.draw.circle(pantalla, color_real, (centro_x, centro_y), radio)
        
        # 2. Indicador de Acción (Brillo alrededor)
        if self.es_actuando:
            pygame.draw.circle(pantalla, AMARILLO_NEON, (centro_x, centro_y), radio + 3, 2)
            
        # 3. Indicador de Tipo de Ficha (Forma/Borde)
        if self.tipo == "pesada":
            # Cuadrado alrededor para 'Fuerte/Pesada'
            rect_pesada = pygame.Rect(centro_x - radio + 1, centro_y - radio + 1, (radio - 1) * 2, (radio - 1) * 2)
            pygame.draw.rect(pantalla, oscurecer_color(color_real, 0.5), rect_pesada, 1)

        elif self.tipo == "ligera":
             # Círculo sencillo para 'Rápida/Ligera'
             pygame.draw.circle(pantalla, NEGRO, (centro_x, centro_y), radio, 1)

        # 4. Indicador para Ficha Perfecta (Emoji)
        if self.tipo == "perfecta":
            # Usar emoji personalizado para la ficha perfecta humana
            if self.color_base == gestor.human_color_base:
                text_surf = FUENTE_EMOJI.render(gestor.perfecta_emoji, True, COLOR_PERFECTA_INDICATOR)
            else:
                # Usar un emoji genérico para IA Perfecta
                text_surf = FUENTE_EMOJI.render("👑", True, COLOR_PERFECTA_INDICATOR)
                
            text_rect = text_surf.get_rect(center=(centro_x, centro_y))
            pantalla.blit(text_surf, text_rect)
        
        # 5. Indicador de inactividad (solo humano)
        if self.color_base == gestor.human_color_base and self.turnos_inactivos > 0:
            if self.tipo == "ligera" and self.turnos_inactivos < 3:
                 text = FUENTE_SMALL.render(f"{self.turnos_inactivos}", True, BLANCO)
                 PANTALLA.blit(text, (centro_x + radio, centro_y - radio))
            elif self.tipo == "pesada" and self.turnos_inactivos < 5:
                 text = FUENTE_SMALL.render(f"{self.turnos_inactivos}", True, BLANCO)
                 PANTALLA.blit(text, (centro_x + radio, centro_y - radio))
        
        # Borde final
        pygame.draw.circle(pantalla, NEGRO, (centro_x, centro_y), radio, 1)


    def mover(self, nueva_fila, nueva_columna):
        self.fila = nueva_fila
        self.columna = nueva_columna

    def obtener_vecinos_libres(self, posiciones_ocupadas):
        vecinos = []
        for r, c in self._obtener_vecinos_adyacentes():
            if (r, c) not in posiciones_ocupadas:
                vecinos.append((r, c))
        return vecinos

    def _obtener_vecinos_adyacentes(self):
        vecinos = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            r, c = self.fila + dr, self.columna + dc
            if 0 <= r < FILAS and 0 <= c < COLUMNAS:
                vecinos.append((r, c))
        return vecinos

    def obtener_oponentes_adyacentes(self, fichas_dict, color_oponente_base):
        oponentes = []
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            pos = (self.fila + dr, self.columna + dc)
            if pos in fichas_dict and fichas_dict[pos].color_base != self.color_base:
                oponentes.append(fichas_dict[pos])
        return oponentes
    
    # **********************************************
    # LÓGICA DE DETECCIÓN DE ENEMIGOS ADYACENTES (BRECHA)
    # **********************************************
    def es_posicion_brecha(self, r, c, fichas_dict):
        """Comprueba si la posición (r, c) es adyacente a un enemigo."""
        for dr, dc in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            pos = (r + dr, c + dc)
            if pos in fichas_dict and fichas_dict[pos].color_base != self.color_base:
                return True
        return False


# --- 4. GESTOR DE JUEGO (Mantiene la lógica) ---

class GestorJuego:
    def __init__(self, player_colors_base, probabilidad_combate, human_color_base=None, human_name="Comandante", perfecta_emoji="⭐"):
        self.fichas = []
        self.mensajes = deque(maxlen=MAX_MENSAJES)
        self.turno_actual = 0
        self.tiempo_inicio = time.time()
        self.tiempo_limite = LIMITE_TIEMPO_SEGUNDOS
        self.player_colors_base = player_colors_base 
        self.probabilidad_combate = probabilidad_combate 
        
        self.estadisticas = {color: {'multiplicaciones': 0, 'movimientos': 0, 'victorias_combate': 0} for color in player_colors_base}
        
        self.human_color_base = human_color_base
        self.human_name = human_name
        self.perfecta_emoji = perfecta_emoji
        self.fichas_perfectas_count = 0
    
    def obtener_nombre_jugador(self, color_base, use_emoji=False):
        """Devuelve el nombre del jugador (nombre_humano o P[N] para IA)."""
        if color_base == self.human_color_base:
            return f"{self.human_name} {self.perfecta_emoji}" if use_emoji else self.human_name
        try:
            idx = COLOR_PALETTE_BASE.index(color_base)
            return f"IA {idx + 1}"
        except ValueError:
            return "???"
            
    def agregar_ficha(self, ficha):
        self.fichas.append(ficha)
    
    def agregar_mensaje(self, mensaje):
        if isinstance(mensaje, tuple): 
            nombre_color = self.obtener_nombre_jugador(mensaje)
            self.mensajes.append(f"[{self.turno_actual:03d}] {nombre_color}")
        else:
            self.mensajes.append(f"[{self.turno_actual:03d}] {mensaje}")

    def obtener_posiciones_ocupadas(self):
        return {(f.fila, f.columna): f for f in self.fichas}
    
    def contar_fichas(self):
        contadores = {color: {'total': 0, 'perfectas': 0} for color in self.player_colors_base}
        for ficha in self.fichas:
            if ficha.color_base in contadores:
                contadores[ficha.color_base]['total'] += 1
                if ficha.tipo == "perfecta":
                    contadores[ficha.color_base]['perfectas'] += 1
        return contadores
    
    def verificar_victoria(self):
        tiempo_transcurrido = time.time() - self.tiempo_inicio
        contadores = self.contar_fichas()
        
        bandos_activos = [color for color, data in contadores.items() if data['total'] > 0]
        
        if len(bandos_activos) == 1:
            return bandos_activos[0]
        elif len(bandos_activos) == 0:
            return AMARILLO_NEON
            
        if tiempo_transcurrido >= self.tiempo_limite:
            if not bandos_activos: return AMARILLO_NEON
            
            max_fichas = max(data['total'] for data in contadores.values())
            lideres = [color for color, data in contadores.items() if data['total'] == max_fichas and data['total'] > 0]
            
            if len(lideres) == 1:
                return lideres[0]
            else:
                return AMARILLO_NEON
                
        return None

    def obtener_estadisticas_finales(self, ganador_color_base):
        contadores = self.contar_fichas()
        
        nombre_ganador = "JUEGO EN CURSO"
        if ganador_color_base:
            if ganador_color_base == AMARILLO_NEON:
                nombre_ganador = "¡EMPATE POR TIEMPO!"
            else:
                nombre_ganador = f"GANADOR: {self.obtener_nombre_jugador(ganador_color_base)}"


        resumen = {
            'ganador_color': ganador_color_base,
            'ganador_nombre': nombre_ganador,
            'contadores': contadores,
            'estadisticas': self.estadisticas,
            'fichas_perfectas_count': self.fichas_perfectas_count
        }
        return resumen

    # (La función de guardar TXT se deja intacta por ser lógica de salida de datos)
    def guardar_resultados_txt(self, resumen):
        output = []
        output.append("=" * 60)
        output.append(f"RESUMEN DE LA GUERRA DE PÍXELES - TURNO FINAL: {self.turno_actual}")
        output.append("=" * 60)
        output.append(f"RESULTADO FINAL: {resumen['ganador_nombre']}")
        output.append(f"PROBABILIDAD COMBATE BASE: {self.probabilidad_combate}") 
        output.append("-" * 60)
        
        for i, color_base in enumerate(self.player_colors_base):
            nombre_color = self.obtener_nombre_jugador(color_base)
                
            data = resumen['contadores'].get(color_base, {'total': 0, 'perfectas': 0})
            stats = resumen['estadisticas'].get(color_base, {})
            
            output.append(f"\nJUGADOR {i+1} - {nombre_color} (RGB: {color_base})")
            output.append(f"  > Fichas TOTALES Finales: {data['total']}")
            output.append(f"  > Fichas PERFECTAS Finales: {data['perfectas']}")
            output.append("  > Estadísticas de Acción:")
            output.append(f"    - Multiplicaciones: {stats.get('multiplicaciones', 0)}")
            output.append(f"    - Movimientos: {stats.get('movimientos', 0)}")
            output.append(f"    - Victorias en Combate: {stats.get('victorias_combate', 0)}")
            output.append("-" * 20)

        try:
            nombre_archivo = "resultados_guerra_pixeles.txt"
            with open(nombre_archivo, "w") as f:
                f.write("\n".join(output))
            print(f"Resultados guardados en {nombre_archivo}")
        except IOError:
            print("ERROR: No se pudo escribir el archivo TXT.")
            
    def tirar_dados(self, num_dados=3):
        return sum(random.randint(1, 6) for _ in range(num_dados))
    
    # (El procesar_turno se deja intacto ya que es la lógica del juego)
    def procesar_turno(self):
        self.turno_actual += 1
        self.agregar_mensaje("=" * 40)
        self.agregar_mensaje(f"TURNO {self.turno_actual} - Total fichas: {len(self.fichas)}")
        
        for ficha in self.fichas:
            ficha.ha_actuado = False
            ficha.es_actuando = False 
            ficha.realizo_accion = False 
        
        fichas_dict = self.obtener_posiciones_ocupadas()
        nuevas_fichas = []
        
        random.shuffle(self.fichas) 
        
        # 2. PROPAGACIÓN DE PERFECCIÓN 
        fichas_dict = self.obtener_posiciones_ocupadas() 
        fichas_propagadas = set() 
        
        for ficha in list(self.fichas):
            if ficha.color_base != self.human_color_base or ficha.tipo != "perfecta" or ficha in fichas_propagadas:
                continue

            if self.fichas_perfectas_count >= MAX_FICHAS_PERFECTAS:
                 break 

            vecinos_adyacentes_pos = ficha._obtener_vecinos_adyacentes()
            random.shuffle(vecinos_adyacentes_pos) 
            
            for r, c in vecinos_adyacentes_pos:
                pos = (r, c)
                if pos in fichas_dict:
                    vecina = fichas_dict[pos]
                    
                    if vecina.color_base == self.human_color_base and vecina.tipo in ["ligera", "pesada"]:
                        
                        tipo_anterior = vecina.tipo
                        vecina.tipo = "perfecta"
                        vecina.dados_combate = 5
                        vecina.puede_mover = True 
                        vecina.turnos_inactivos = 0 
                        self.fichas_perfectas_count += 1
                        fichas_propagadas.add(vecina)
                        
                        nombre_humano = self.obtener_nombre_jugador(self.human_color_base, use_emoji=True)
                        self.agregar_mensaje(f"👑 {nombre_humano} propaga a {tipo_anterior.upper()}!")
                        break 
        
        # 3. Bucle principal de acción de fichas
        for ficha in list(self.fichas):
            if ficha.ha_actuado or ficha.color_base not in self.player_colors_base: 
                continue
            
            ficha.es_actuando = True 
            nombre_propio = self.obtener_nombre_jugador(ficha.color_base)
            
            # 3.1. COMBATE (prioridad máxima)
            oponentes = ficha.obtener_oponentes_adyacentes(fichas_dict, None) 
            
            if oponentes:
                oponente = random.choice(oponentes)

                is_ficha_perfecta = (ficha.tipo == "perfecta")
                is_oponente_perfecta = (oponente.tipo == "perfecta")

                if is_ficha_perfecta and not is_oponente_perfecta:
                    puntuacion_propia = 9999 
                    puntuacion_oponente = 0
                elif is_oponente_perfecta and not is_ficha_perfecta:
                    puntuacion_propia = 0
                    puntuacion_oponente = 9999 
                else:
                    puntuacion_propia = self.tirar_dados(ficha.dados_combate)
                    puntuacion_oponente = self.tirar_dados(oponente.dados_combate)
                
                nombre_oponente = self.obtener_nombre_jugador(oponente.color_base)
                
                if puntuacion_propia > puntuacion_oponente:
                    color_ganador_base = ficha.color_base
                    tipo_ganador = "pesada" if ficha.tipo == "perfecta" else ficha.tipo 
                    ficha_perdedora = oponente
                    
                    ficha.realizo_accion = True 
                    ficha_perdedora.realizo_accion = True 
                
                elif puntuacion_oponente > puntuacion_propia:
                    color_ganador_base = oponente.color_base
                    tipo_ganador = "pesada" if oponente.tipo == "perfecta" else oponente.tipo
                    ficha_perdedora = ficha
                    
                    oponente.realizo_accion = True 
                    ficha_perdedora.realizo_accion = True 
                
                else: # Empate
                    self.agregar_mensaje(f"⚔️ {nombre_propio} vs {nombre_oponente} -> EMPATE ({puntuacion_propia}/{puntuacion_oponente})")
                    ficha.ha_actuado = True
                    oponente.ha_actuado = True
                    ficha.es_actuando = False 
                    oponente.es_actuando = False 
                    continue
                
                if ficha_perdedora.tipo == "perfecta" and ficha_perdedora.color_base == self.human_color_base:
                     self.fichas_perfectas_count -= 1 

                ficha_perdedora.color_base = color_ganador_base
                ficha_perdedora.tipo = tipo_ganador
                self.estadisticas[color_ganador_base]['victorias_combate'] += 1 
                
                nombre_ganador = self.obtener_nombre_jugador(color_ganador_base)
                nombre_perdedor = self.obtener_nombre_jugador(ficha_perdedora.color_base)
                self.agregar_mensaje(f"⚔️ {nombre_ganador} GANA y tiñe a {nombre_perdedor} en {tipo_ganador[0].upper()}")

                ficha.ha_actuado = True
                oponente.ha_actuado = True
                ficha.es_actuando = False
                oponente.es_actuando = False
                continue
            
            # 3.2. REEMPLAZO TÁCTICO Y ASALTO INMEDIATO (SOLO Ficha Perfecta Humana)
            if ficha.tipo == "perfecta" and ficha.color_base == self.human_color_base:
                vecinos_adyacentes_pos = ficha._obtener_vecinos_adyacentes()
                aliados_adyacentes = []
                
                for r, c in vecinos_adyacentes_pos:
                    pos = (r, c)
                    if pos in fichas_dict:
                        aliada = fichas_dict[pos]
                        if aliada.color_base == ficha.color_base and aliada.tipo in ["ligera", "pesada"] and not aliada.ha_actuado:
                            aliados_adyacentes.append(aliada)
                
                if aliados_adyacentes:
                    aliada_a_reemplazar = random.choice(aliados_adyacentes)
                    
                    pos_perfecta_vieja = (ficha.fila, ficha.columna)
                    pos_perfecta_nueva = (aliada_a_reemplazar.fila, aliada_a_reemplazar.columna)
                    
                    ficha.mover(pos_perfecta_nueva[0], pos_perfecta_nueva[1])
                    aliada_a_reemplazar.mover(pos_perfecta_vieja[0], pos_perfecta_vieja[1])
                    
                    fichas_dict[pos_perfecta_nueva] = ficha
                    fichas_dict[pos_perfecta_vieja] = aliada_a_reemplazar
                    
                    ficha.realizo_accion = True
                    ficha.ha_actuado = True
                    aliada_a_reemplazar.ha_actuado = True 
                    
                    self.estadisticas[ficha.color_base]['movimientos'] += 1 
                    self.agregar_mensaje(f"🔄 {nombre_propio} PERFECTA hace Reemplazo Táctico con aliada {aliada_a_reemplazar.tipo[0].upper()}!")

                    oponentes_nuevos = ficha.obtener_oponentes_adyacentes(fichas_dict, None) 
                    
                    if oponentes_nuevos:
                        oponente_atacado = random.choice(oponentes_nuevos)
                        nombre_oponente_atacado = self.obtener_nombre_jugador(oponente_atacado.color_base)
                        
                        if oponente_atacado.tipo != "perfecta":
                            ficha_perdedora = oponente_atacado
                            color_ganador_base = ficha.color_base
                            tipo_ganador = "pesada" 

                            ficha_perdedora.color_base = color_ganador_base
                            ficha_perdedora.tipo = tipo_ganador
                            self.estadisticas[color_ganador_base]['victorias_combate'] += 1 
                            
                            nombre_ganador = self.obtener_nombre_jugador(color_ganador_base)
                            self.agregar_mensaje(f"💥 {nombre_ganador} PERFECTA TOMA POSICIÓN y tiñe a {nombre_oponente_atacado}!")

                            oponente_atacado.ha_actuado = True 
                        
                        else:
                             puntuacion_propia = self.tirar_dados(ficha.dados_combate)
                             puntuacion_oponente = self.tirar_dados(oponente_atacado.dados_combate)
                             
                             if puntuacion_propia > puntuacion_oponente:
                                 ficha_perdedora = oponente_atacado
                                 color_ganador_base = ficha.color_base
                                 tipo_ganador = "pesada"
                                 
                                 if ficha_perdedora.tipo == "perfecta" and ficha_perdedora.color_base == self.human_color_base:
                                     self.fichas_perfectas_count -= 1 
                                     
                                 ficha_perdedora.color_base = color_ganador_base
                                 ficha_perdedora.tipo = tipo_ganador
                                 self.estadisticas[color_ganador_base]['victorias_combate'] += 1
                                 self.agregar_mensaje(f"⚔️ {nombre_propio} GANA (PERF vs PERF) en Brecha! {nombre_oponente_atacado} teñido a FUERTE.")
                             else:
                                self.agregar_mensaje(f"⚔️ {nombre_propio} EMPATE (PERF vs PERF) en Brecha.")
                                oponente_atacado.ha_actuado = True
                    
                    ficha.es_actuando = False
                    continue 

            
            # 3.3. ACCIÓN ESTÁNDAR (Mover o Multiplicar)
            vecinos_libres = ficha.obtener_vecinos_libres(set(fichas_dict.keys()))
            
            if not vecinos_libres:
                ficha.ha_actuado = True
                ficha.es_actuando = False
                continue
            
            conteo_propio = self.contar_fichas().get(ficha.color_base, {}).get('total', 0)
            max_fichas_total = COLUMNAS * FILAS 
            probabilidad_multiplicar_frente = self.probabilidad_combate + (conteo_propio / max_fichas_total)
            
            
            if not ficha.puede_mover:
                 accion = "multiplicar"
            else:
                 accion = "mover" if random.random() < probabilidad_multiplicar_frente else "multiplicar"

            if accion == "multiplicar":
                
                tipos_generados = []
                accion_msg = ""
                is_human_unit = (ficha.color_base == self.human_color_base)
                
                if ficha.tipo == "ligera": 
                    if random.random() < 0.5: 
                        tipos_generados = ["ligera"] * 3
                        accion_msg = "x3 Rápidas"
                    else: 
                        tipos_generados = ["pesada"] * 1
                        accion_msg = "x1 Fuerte"
                
                elif ficha.tipo == "pesada": 
                    
                    if is_human_unit:
                        if random.random() < 0.5: 
                            tipos_generados = ["pesada"] * 2
                            accion_msg = "x2 Fuertes"
                        else: 
                            tipos_generados = ["ligera"] * 4
                            accion_msg = "x4 Rápidas"
                            
                        if self.fichas_perfectas_count < MAX_FICHAS_PERFECTAS:
                            if tipos_generados and tipos_generados[0] != "perfecta":
                                tipos_generados[0] = "perfecta" 
                                accion_msg += f" + 1 {self.perfecta_emoji}"
                    else:
                        if random.random() < 0.6: 
                            tipos_generados = ["pesada", "ligera", "ligera"] 
                            accion_msg = "x3 (1F, 2R)"
                        else: 
                            tipos_generados = ["pesada"] * 3 
                            accion_msg = "x3 Fuertes"

                else: # ficha.tipo == "perfecta"
                    if self.fichas_perfectas_count < MAX_FICHAS_PERFECTAS:
                        tipos_generados = ["perfecta", "pesada", "ligera"]
                        accion_msg = f"x1 {self.perfecta_emoji}, x1 Fuerte, x1 Rápida"
                    else:
                        tipos_generados = ["pesada"] * 2
                        accion_msg = "x2 Fuertes"
                
                posiciones_disponibles = ficha.obtener_vecinos_libres(set(fichas_dict.keys()))
                num_a_generar = len(tipos_generados)
                
                posiciones_generadas = random.sample(posiciones_disponibles, min(num_a_generar, len(posiciones_disponibles)))
                
                if posiciones_generadas: 
                    ficha.realizo_accion = True 
                    
                    for i, pos in enumerate(posiciones_generadas):
                        if i < len(tipos_generados): 
                            r_new, c_new = pos
                            nuevo_tipo = tipos_generados[i]
                            
                            if nuevo_tipo == "perfecta":
                                self.fichas_perfectas_count += 1
                            
                            nueva_ficha = Ficha(ficha.color_base, r_new, c_new, tipo=nuevo_tipo)
                            nueva_ficha.ha_actuado = True 
                            nuevas_fichas.append(nueva_ficha)
                            fichas_dict[pos] = nueva_ficha
                    
                    self.estadisticas[ficha.color_base]['multiplicaciones'] += 1 
                    self.agregar_mensaje(f"➕ {nombre_propio} se multiplica ({ficha.tipo[0].upper()} -> {accion_msg}, {len(posiciones_generadas)} creadas)")
            
            elif accion == "mover" and ficha.puede_mover:
                
                r_new, c_new = ficha.fila, ficha.columna
                
                # **********************************************
                # LÓGICA DE MOVIMIENTO TÁCTICO PARA PERFECTA HUMANA
                # **********************************************
                if ficha.tipo == "perfecta" and ficha.color_base == self.human_color_base:
                    
                    # 1. Buscar posiciones libres adyacentes a un enemigo
                    posiciones_brecha = [pos for pos in vecinos_libres if ficha.es_posicion_brecha(pos[0], pos[1], fichas_dict)]
                    
                    if posiciones_brecha:
                        # Prioridad 1: Mover a posición de brecha
                        r_new, c_new = random.choice(posiciones_brecha)
                        self.agregar_mensaje(f"➡️ {nombre_propio} PERFECTA Abre Brecha!")
                    else:
                        # Prioridad 2: Movimiento aleatorio (expansión)
                        r_new, c_new = random.choice(vecinos_libres) 
                        self.agregar_mensaje(f"↗️ {nombre_propio} PERFECTA Avanza")
                
                else: 
                    # Movimiento aleatorio para el resto de unidades móviles (Ligera y Perfecta IA)
                    r_new, c_new = random.choice(vecinos_libres)
                    self.agregar_mensaje(f"↗️ {nombre_propio} RÁPIDA/PERFECTA IA se mueve")

                del fichas_dict[(ficha.fila, ficha.columna)]
                ficha.mover(r_new, c_new)
                fichas_dict[(r_new, c_new)] = ficha
                self.estadisticas[ficha.color_base]['movimientos'] += 1 
                ficha.realizo_accion = True 
            
            ficha.ha_actuado = True
            ficha.es_actuando = False 
        
        
        # 4. PROCESAR INACTIVIDAD Y ASCENSO DE FICHAS HUMANAS
        for ficha in self.fichas:
            if ficha.color_base != self.human_color_base:
                continue
                
            if ficha.realizo_accion: 
                ficha.turnos_inactivos = 0 
            else:
                ficha.turnos_inactivos += 1
                
                nombre_humano = self.obtener_nombre_jugador(self.human_color_base)
                
                if ficha.tipo == "ligera" and ficha.turnos_inactivos >= 3:
                    ficha.tipo = "pesada"
                    ficha.dados_combate = 5 
                    ficha.puede_mover = False 
                    ficha.turnos_inactivos = 0
                    self.agregar_mensaje(f"⭐ {nombre_humano} Rápida ASCIENDE a Fuerte por inactividad!")
                
                elif ficha.tipo == "pesada" and ficha.turnos_inactivos >= 5:
                    if self.fichas_perfectas_count < MAX_FICHAS_PERFECTAS:
                        ficha.tipo = "perfecta"
                        ficha.dados_combate = 5
                        ficha.puede_mover = True 
                        ficha.turnos_inactivos = 0
                        self.fichas_perfectas_count += 1
                        self.agregar_mensaje(f"{self.perfecta_emoji} {nombre_humano} Fuerte ASCIENDE a PERFECTA por inactividad!")
                    else:
                        pass 

        self.fichas_perfectas_count = sum(1 for f in self.fichas if f.color_base == self.human_color_base and f.tipo == "perfecta")
        
        self.fichas.extend(nuevas_fichas)
        self.fichas = [f for f in self.fichas if f.color_base in self.player_colors_base]
        
        return self.verificar_victoria()

# --- 5. FUNCIONES DE DIBUJO ---

def dibujar_cuadricula():
    """Dibuja la cuadrícula solo en el área del tablero."""
    for x in range(0, ANCHO_TABLERO + 1, TAMANO_CELDA):
        pygame.draw.line(PANTALLA, GRIS_CUADRICULA, (x, 0), (x, ALTO_PANTALLA))
    for y in range(0, ALTO_PANTALLA + 1, TAMANO_CELDA):
        pygame.draw.line(PANTALLA, GRIS_CUADRICULA, (0, y), (ANCHO_TABLERO, y))

def dibujar_resumen_final(gestor, resumen, boton_cerrar):
    """Dibuja la pantalla final con estilo mejorado."""
    PANTALLA.fill(NEGRO_FONDO) 
    
    texto_titulo = FUENTE_GANADOR.render("FIN DE LA GUERRA", True, ROJO_ALERTA)
    PANTALLA.blit(texto_titulo, (ANCHO_PANTALLA // 2 - texto_titulo.get_width() // 2, 20))

    texto_ganador = FUENTE_TITULO_GRANDE.render(resumen['ganador_nombre'], True, AMARILLO_NEON)
    PANTALLA.blit(texto_ganador, (ANCHO_PANTALLA // 2 - texto_ganador.get_width() // 2, 80))
    
    pygame.draw.line(PANTALLA, GRIS_CUADRICULA, (50, 150), (ANCHO_PANTALLA - 50, 150), 2)
    
    x_start = 50
    y_start = 180
    col_width = (ANCHO_PANTALLA - 100) // 4 
    
    for i, color_base in enumerate(gestor.player_colors_base):
        if i >= 8: break 
        
        x_pos = x_start + (i % 4) * col_width
        y_pos = y_start + (i // 4) * 250

        nombre = gestor.obtener_nombre_jugador(color_base)

        data = resumen['contadores'].get(color_base, {'total': 0, 'perfectas': 0})
        stats = resumen['estadisticas'].get(color_base, {})
        
        fichas_rap = sum(1 for f in gestor.fichas if f.color_base == color_base and f.tipo == "ligera")
        fichas_fue = sum(1 for f in gestor.fichas if f.color_base == color_base and f.tipo == "pesada")
        fichas_perf = data['perfectas'] 

        # Marco del jugador
        pygame.draw.rect(PANTALLA, oscurecer_color(color_base, 0.5), (x_pos - 5, y_pos - 5, col_width - 10, 230), border_radius=5)
        
        texto_nombre = FUENTE_TITULO.render(f"JUGADOR: {nombre}", True, color_base) 
        PANTALLA.blit(texto_nombre, (x_pos, y_pos))

        texto_conteo = FUENTE_ESTADISTICAS.render(f"TOTAL Fichas: {data['total']}", True, BLANCO) 
        PANTALLA.blit(texto_conteo, (x_pos, y_pos + 40))

        # Tipos de ficha
        texto_rapida = FUENTE_PRINCIPAL.render(f"  Rápidas (L): {fichas_rap}", True, BLANCO)
        PANTALLA.blit(texto_rapida, (x_pos, y_pos + 70))
        
        texto_fuerte = FUENTE_PRINCIPAL.render(f"  Fuertes (P): {fichas_fue}", True, BLANCO)
        PANTALLA.blit(texto_fuerte, (x_pos, y_pos + 95))

        if fichas_perf > 0:
            emoji_display = gestor.perfecta_emoji if color_base == gestor.human_color_base else "👑"
            texto_perf = FUENTE_PRINCIPAL.render(f"  PERFECTAS ({emoji_display}): {fichas_perf}", True, COLOR_PERFECTA_INDICATOR)
            PANTALLA.blit(texto_perf, (x_pos, y_pos + 120))


        y_offset = y_pos + 155
        texto_combate = FUENTE_PRINCIPAL.render(f"Victorias Combate: {stats.get('victorias_combate', 0)}", True, BLANCO)
        PANTALLA.blit(texto_combate, (x_pos, y_offset))
        y_offset += 20
        
        texto_mult = FUENTE_PRINCIPAL.render(f"Multiplicaciones: {stats.get('multiplicaciones', 0)}", True, BLANCO)
        PANTALLA.blit(texto_mult, (x_pos, y_offset))
            
    # Dibujar el botón de cierre
    boton_cerrar.draw(PANTALLA)

    pygame.display.flip()


def dibujar_interfaz(gestor, velocidad_actual, es_pausado, botones_velocidad):
    """Dibuja la interfaz de juego con el panel lateral mejorado."""
    PANTALLA.fill(VERDE_TABLERO)
    
    # 1. Dibujar el Tablero y Fichas
    pygame.draw.rect(PANTALLA, VERDE_TABLERO, (0, 0, ANCHO_TABLERO, ALTO_PANTALLA))
    dibujar_cuadricula()
    
    for ficha in gestor.fichas:
        ficha.dibujar(PANTALLA)
    
    # 2. Dibujar el Panel Lateral (HUD)
    panel_rect = pygame.Rect(ANCHO_TABLERO, 0, ANCHO_PANEL_DERECHO, ALTO_PANTALLA)
    pygame.draw.rect(PANTALLA, NEGRO_FONDO, panel_rect)
    pygame.draw.line(PANTALLA, AMARILLO_NEON, (ANCHO_TABLERO, 0), (ANCHO_TABLERO, ALTO_PANTALLA), 3)

    contadores = gestor.contar_fichas()
    
    # Título del HUD
    titulo_hud = FUENTE_TITULO.render("Estadísticas", True, AMARILLO_NEON)
    PANTALLA.blit(titulo_hud, (ANCHO_TABLERO + 10, 10))
    pygame.draw.line(PANTALLA, GRIS_CUADRICULA, (ANCHO_TABLERO + 10, 40), (ANCHO_PANTALLA - 10, 40), 1)
    
    # 3. Contadores principales y Stats
    y_count = 50
    for color_base in gestor.player_colors_base:
        if color_base not in contadores: continue
        
        data = contadores[color_base]
        nombre = gestor.obtener_nombre_jugador(color_base)
        
        # Nombre y Total
        texto_nombre_total = FUENTE_ESTADISTICAS.render(f"{nombre}: {data['total']}", True, color_base)
        PANTALLA.blit(texto_nombre_total, (ANCHO_TABLERO + 10, y_count))
        y_count += 20
        
        # Tipos de ficha
        fichas_rap = sum(1 for f in gestor.fichas if f.color_base == color_base and f.tipo == "ligera")
        fichas_fue = sum(1 for f in gestor.fichas if f.color_base == color_base and f.tipo == "pesada")
        fichas_perf = data['perfectas']
        
        texto_tipos = FUENTE_PRINCIPAL.render(f"  R:{fichas_rap} | F:{fichas_fue}", True, BLANCO)
        PANTALLA.blit(texto_tipos, (ANCHO_TABLERO + 10, y_count))
        
        if fichas_perf > 0:
            emoji_display = gestor.perfecta_emoji if color_base == gestor.human_color_base else "👑"
            texto_perf = FUENTE_EMOJI.render(f"{emoji_display}:{fichas_perf}", True, COLOR_PERFECTA_INDICATOR)
            PANTALLA.blit(texto_perf, (ANCHO_TABLERO + 150, y_count))
        
        y_count += 25 
        
        # Victorias de combate
        victorias = gestor.estadisticas.get(color_base, {}).get('victorias_combate', 0)
        texto_vict = FUENTE_SMALL.render(f"Vict. Combate: {victorias}", True, BLANCO)
        PANTALLA.blit(texto_vict, (ANCHO_TABLERO + 10, y_count))
        
        # Límite de Perfectas (solo humano)
        if color_base == gestor.human_color_base:
             texto_limite = FUENTE_SMALL.render(f"Límite {gestor.perfecta_emoji}: {MAX_FICHAS_PERFECTAS - gestor.fichas_perfectas_count}", True, COLOR_PERFECTA_INDICATOR)
             PANTALLA.blit(texto_limite, (ANCHO_TABLERO + 10, y_count + 15))
             y_count += 30 
        
        y_count += 20
        pygame.draw.line(PANTALLA, GRIS_CUADRICULA, (ANCHO_TABLERO + 10, y_count), (ANCHO_PANTALLA - 10, y_count), 1)
        y_count += 10

    # 4. Cronómetro y Turno
    tiempo_restante = max(0, gestor.tiempo_limite - (time.time() - gestor.tiempo_inicio))
    minutos = int(tiempo_restante // 60)
    segundos = int(tiempo_restante % 60)
    color_tiempo = ROJO_ALERTA if tiempo_restante < 60 and tiempo_restante > 0 else AMARILLO_NEON
    
    texto_tiempo = FUENTE_CRONOMETRO.render(f"{minutos:02}:{segundos:02}", True, color_tiempo)
    PANTALLA.blit(texto_tiempo, (ANCHO_TABLERO + 10, ALTO_PANTALLA - 150))
    
    texto_turno = FUENTE_TITULO.render(f"Turno: {gestor.turno_actual:04d}", True, BLANCO)
    PANTALLA.blit(texto_turno, (ANCHO_TABLERO + 10, ALTO_PANTALLA - 100))
    
    # 5. Controles de Velocidad 
    y_control = ALTO_PANTALLA - 50 
    
    texto_velocidad = FUENTE_PRINCIPAL.render("VELOCIDAD:", True, BLANCO)
    PANTALLA.blit(texto_velocidad, (ANCHO_TABLERO + 10, y_control - 20))
    
    for btn in botones_velocidad:
        is_selected = (es_pausado and btn.text == "⏸") or \
                      (not es_pausado and btn.action == velocidad_actual and btn.text != "⏸")
        btn.draw(PANTALLA, is_selected=is_selected)

    # 6. Mensajes del turno (en el lado izquierdo del tablero)
    y_offset = ALTO_PANTALLA - 20
    for mensaje in gestor.mensajes:
        texto_msg = FUENTE_PRINCIPAL.render(mensaje, True, BLANCO, (0,0,0,100)) # Fondo semitransparente para mejor lectura
        PANTALLA.blit(texto_msg, (10, y_offset))
        y_offset -= 18
    
    pygame.display.flip()


# --- 6. MENÚ PRINCIPAL MEJORADO ESTÉTICAMENTE ---

def menu_principal():
    corriendo = True
    num_oponentes = 1 
    human_color_base = COLOR_PALETTE_BASE[0] 
    probabilidad_combate = PROBABILIDAD_COMBATE_BASE 
    human_name = "Comandante"
    
    # --- POSICIONES Y TAMAÑOS ---
    center_x = ANCHO_PANTALLA // 2
    
    # INPUT NOMBRE
    input_rect_name = pygame.Rect(center_x - 200, 320, 400, 35)
    input_active_name = False
    color_inactive = GRIS_OSCURO_HUD
    color_active = (50, 50, 70)

    # TITULO
    titulo = FUENTE_TITULO_GRANDE.render("GUERRA DE PÍXELES - CONFIGURACIÓN", True, AMARILLO_NEON)
    
    # 1. CONFIGURACIÓN DEL JUGADOR
    subtitulo_jugador = FUENTE_TITULO.render("1. ELIGE TU UNIDAD COMANDANTE:", True, BLANCO)
    
    buttons_colores = []
    btn_size = 40
    start_x = center_x - (btn_size * 4 + 10 * 3) 
    
    for i, color in enumerate(COLOR_PALETTE_BASE):
        btn = Button(start_x + (i % 4) * (btn_size + 10), 200 + (i // 4) * 50, btn_size, btn_size, f"P{i+1}", color)
        btn.action = color
        buttons_colores.append(btn)
        
    # 2. CONFIGURACIÓN DE OPONENTES Y EMOJI
    subtitulo_oponentes = FUENTE_TITULO.render("2. NOMBRE, EMOJI y OPONENTES:", True, BLANCO)
    
    # Dropdown para el Emoji
    dropdown_emoji = Dropdown(
        center_x - 200, 
        370, 
        400, 
        35, 
        "Emoji Perfecta", 
        EMOJI_OPTIONS, 
        FUENTE_PRINCIPAL,
        FUENTE_EMOJI
    )
    
    buttons_oponentes = []
    btn_width = 40
    btn_height = 35
    start_x_op = center_x - (btn_width * 4 + 10 * 3) 
    
    for i in range(1, 8):
        btn = Button(start_x_op + (i-1) * (btn_width + 10), 460, btn_width, btn_height, str(i), COLOR_BOTON_NORMAL)
        btn.action = i
        buttons_oponentes.append(btn)
        
    # 3. CONFIGURACIÓN DE AGRESIVIDAD
    subtitulo_combate = FUENTE_TITULO.render("3. PROBABILIDAD DE COMBATE:", True, BLANCO)
    
    buttons_combate = []
    valores_combate = [0.3, 0.5, 0.7, 0.9]
    nombres_combate = ["Baja (30%)", "Media (50%)", "Alta (70%)", "Locura (90%)"]
    btn_width_c = 150
    start_x_c = center_x - (btn_width_c * 2 + 10) 
    
    for i, val in enumerate(valores_combate):
        btn = Button(start_x_c + (i % 2) * (btn_width_c + 10), 600 + (i // 2) * 45, btn_width_c, btn_height, nombres_combate[i], COLOR_BOTON_NORMAL)
        btn.action = val
        buttons_combate.append(btn)
        
    start_button = Button(
        ANCHO_PANTALLA - 200,
        ALTO_PANTALLA - 60,
        150,
        40,
        "INICIAR",
        (0, 200, 0)
    )

    while corriendo:
        PANTALLA.fill(NEGRO_FONDO)
        PANTALLA.blit(titulo, (center_x - titulo.get_width() // 2, 30))

        # Dibujar secciones
        PANTALLA.blit(subtitulo_jugador, (center_x - subtitulo_jugador.get_width() // 2, 160))
        PANTALLA.blit(subtitulo_oponentes, (center_x - subtitulo_oponentes.get_width() // 2, 280))
        PANTALLA.blit(subtitulo_combate, (center_x - subtitulo_combate.get_width() // 2, 560))
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            
            # Manejar input de texto y clicks
            if event.type == pygame.MOUSEBUTTONDOWN:
                if dropdown_emoji.handle_event(event):
                    input_active_name = False 
                    continue 

                if input_rect_name.collidepoint(event.pos):
                    input_active_name = True
                else:
                    input_active_name = False
            
            if event.type == pygame.KEYDOWN:
                if input_active_name:
                    if event.key == pygame.K_RETURN:
                        input_active_name = False
                    elif event.key == pygame.K_BACKSPACE:
                        human_name = human_name[:-1]
                    else:
                        if len(human_name) < 15:
                             human_name += event.unicode


            # Manejar clicks de botones
            for btn in buttons_colores:
                if btn.is_clicked(event):
                    human_color_base = btn.action
            
            for btn in buttons_oponentes:
                if btn.is_clicked(event):
                    num_oponentes = btn.action
            
            for btn in buttons_combate:
                if btn.is_clicked(event):
                    probabilidad_combate = btn.action
            
            if start_button.is_clicked(event):
                corriendo = False

        # Dibujar Input Fields (Nombre)
        color_name = color_active if input_active_name else color_inactive
        pygame.draw.rect(PANTALLA, color_name, input_rect_name, 0, border_radius=5)
        
        # Texto de etiqueta
        label_surf = FUENTE_PRINCIPAL.render("Nombre:", True, BLANCO)
        PANTALLA.blit(label_surf, (input_rect_name.x + 5, input_rect_name.y + 7))

        # Nombre del jugador
        text_surface_name = FUENTE_PRINCIPAL.render(human_name, True, AMARILLO_NEON)
        PANTALLA.blit(text_surface_name, (input_rect_name.x + 90, input_rect_name.y + 7))
        
        # Dibujar Dropdown
        dropdown_emoji.draw(PANTALLA)

        # Dibujar botones y resaltar el seleccionado
        for btn in buttons_colores:
            btn.draw(PANTALLA, is_selected=(btn.action == human_color_base))
        
        for btn in buttons_oponentes:
            btn.draw(PANTALLA, is_selected=(btn.action == num_oponentes))
            
        for btn in buttons_combate:
            btn.draw(PANTALLA, is_selected=(btn.action == probabilidad_combate))
        
        start_button.draw(PANTALLA)
        
        pygame.display.flip()
        RELOJ.tick(60)
        
    oponent_colors = [c for c in COLOR_PALETTE_BASE if c != human_color_base][:num_oponentes]
    all_player_colors = [human_color_base] + oponent_colors
    
    return all_player_colors, probabilidad_combate, human_color_base, human_name.strip()[:15], dropdown_emoji.selected_option

# --- 7. BUCLE PRINCIPAL (FINAL) ---

def main():
    all_player_colors, probabilidad_combate, human_color_base, human_name, perfecta_emoji = menu_principal()

    global gestor 
    gestor = GestorJuego(all_player_colors, probabilidad_combate, human_color_base, human_name, perfecta_emoji) 
    
    # Generar posiciones iniciales dispersas para N jugadores
    initial_positions = [
        (0, 0), (FILAS - 1, COLUMNAS - 1), (FILAS - 1, 0), (0, COLUMNAS - 1),                          
        (FILAS // 2, 0), (FILAS // 2, COLUMNAS - 1), (0, COLUMNAS // 2), (FILAS - 1, COLUMNAS // 2)                  
    ]
    
    # Asignar fichas iniciales
    for i, color_base in enumerate(all_player_colors):
        r, c = initial_positions[i]
        ficha_tipo_1 = "pesada" 
        ficha_tipo_2 = "ligera" 
        
        gestor.agregar_ficha(Ficha(color_base, r, c, tipo=ficha_tipo_1))
        
        r2, c2 = r + 1, c
        if 0 <= r2 < FILAS and 0 <= c2 < COLUMNAS and (r2, c2) != (r, c):
             gestor.agregar_ficha(Ficha(color_base, r2, c2, tipo=ficha_tipo_2))

    
    ultimo_turno = pygame.time.get_ticks()
    corriendo = True
    ganador = None
    
    velocidad_actual = 1
    es_pausado = False
    
    # Creamos los botones de velocidad/pausa
    velocidades = [
        ("⏸", 0, ROJO_ALERTA), 
        ("1x", 1, AZUL_CLARO), 
        ("2x", 2, AZUL_CLARO), 
        ("4x", 4, AZUL_CLARO), 
        ("8x", 8, AZUL_CLARO),
        ("16x", 16, AZUL_CLARO), 
        ("32x", 32, AZUL_CLARO), 
        ("64x", 64, AZUL_CLARO), 
        ("128x", 128, AZUL_CLARO), 
        ("256x", 256, AZUL_CLARO)
    ]
    btn_width = 50
    btn_height = 25
    
    # Calcular posición para que quepan en el panel derecho
    start_x = ANCHO_TABLERO + 10
    
    botones_velocidad = []
    current_x = start_x
    y_pos = ALTO_PANTALLA - 50 
    
    for i, (text, speed, color) in enumerate(velocidades):
        if i > 0 and i % 5 == 0: # 5 botones por fila
            current_x = start_x
            y_pos += btn_height + 5
            
        btn = Button(current_x, y_pos, btn_width, btn_height, text, color, action=speed)
        botones_velocidad.append(btn)
        current_x += btn_width + 5


    while corriendo:
        for evento in pygame.event.get():
            if evento.type == pygame.QUIT:
                corriendo = False
            
            for btn in botones_velocidad:
                if btn.is_clicked(evento):
                    if btn.text == "⏸":
                        es_pausado = not es_pausado
                    else:
                        es_pausado = False
                        velocidad_actual = btn.action
                        if velocidad_actual == 0:
                            velocidad_actual = 1 

            if evento.type == pygame.KEYDOWN:
                 if evento.key == pygame.K_SPACE:
                    if es_pausado:
                        ganador = gestor.procesar_turno()
                        if ganador:
                            corriendo = False
                 if evento.key == pygame.K_ESCAPE:
                    corriendo = False
        
        tiempo_actual = pygame.time.get_ticks()
        
        if not es_pausado and not ganador:
            turn_delay = BASE_TIEMPO_ENTRE_TURNOS / velocidad_actual
            
            if (tiempo_actual - ultimo_turno >= turn_delay):
                ganador = gestor.procesar_turno()
                dibujar_interfaz(gestor, velocidad_actual, es_pausado, botones_velocidad) 
                ultimo_turno = tiempo_actual
                
                if ganador:
                    corriendo = False
        
        if corriendo and time.time() - gestor.tiempo_inicio >= gestor.tiempo_limite:
            ganador = gestor.verificar_victoria()
            corriendo = False

        if corriendo:
            dibujar_interfaz(gestor, velocidad_actual, es_pausado, botones_velocidad)
        else:
            break
        
        RELOJ.tick(60)
    
    # -------------------------------------------------------------
    # BUCLE PARA PANTALLA DE RESULTADOS
    # -------------------------------------------------------------
    if ganador:
        resumen_final = gestor.obtener_estadisticas_finales(ganador)
        gestor.guardar_resultados_txt(resumen_final)

        mostrar_resumen = True
        
        BTN_CERRAR = Button(
            ANCHO_PANTALLA // 2 - 150,
            ALTO_PANTALLA - 60,
            300,
            40,
            "CERRAR JUEGO (ESC/Click)",
            ROJO_ALERTA
        )
        
        while mostrar_resumen:
            for evento in pygame.event.get():
                if evento.type == pygame.QUIT:
                    mostrar_resumen = False
                
                if BTN_CERRAR.is_clicked(evento):
                    mostrar_resumen = False
                    
                if evento.type == pygame.KEYDOWN and evento.key == pygame.K_ESCAPE:
                    mostrar_resumen = False

            dibujar_resumen_final(gestor, resumen_final, BTN_CERRAR) 
            RELOJ.tick(60)
    
    pygame.quit()

if __name__ == "__main__":
    main()