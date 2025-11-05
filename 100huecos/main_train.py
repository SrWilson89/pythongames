# main_train.py (Versión Final con Ventana de Registro Separada)

import numpy as np
import tkinter as tk
from tkinter import scrolledtext, messagebox, simpledialog, ttk
import os
import time
import sys
import colorsys
import threading

# --- Importación de Clases de Entorno y Agente ---
try:
    from environment import CaballoTourEnvironment
    from agent_dqn import DQNAgent
except ImportError:
    print("Error de Importación: Asegúrate de que 'environment.py' y 'agent_dqn.py' están en la misma carpeta.")
    sys.exit(1)

# ----------------------------------------------------------------------
# 0. CONSTANTES GLOBALES
# ----------------------------------------------------------------------
DEFAULT_WINDOW_WIDTH = 800
DEFAULT_WINDOW_HEIGHT = 600
TARGET_UPDATE_FREQ = 10  
TOP_N_SAVES = 5  
STABLE_UPDATE_INTERVAL = 30.0  

# ----------------------------------------------------------------------
# 0. UTILIDADES DE VENTANA
# ----------------------------------------------------------------------

def configure_window(window, width=DEFAULT_WINDOW_WIDTH, height=DEFAULT_WINDOW_HEIGHT, resizable=False):
    """
    Configura la ventana con tamaño fijo, centrado y toggle de pantalla completa (F11/Escape).
    """
    # 1. Establecer el tamaño y centrado
    window.geometry(f"{width}x{height}")
    if not resizable:
        window.resizable(False, False)
    
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x_c = (screen_width // 2) - (width // 2)
    y_c = (screen_height // 2) - (height // 2)
    window.geometry(f'+{x_c}+{y_c}')
    
    # 2. Función para alternar pantalla completa
    def toggle_fullscreen(event=None):
        is_fullscreen = window.attributes('-fullscreen')
        window.attributes('-fullscreen', not is_fullscreen)
    
    # 3. Enlazar teclas a la ventana específica
    window.bind('<F11>', toggle_fullscreen)
    window.bind('<Escape>', toggle_fullscreen)
    
def format_time(seconds):
    """Formatea la duración en segundos a Hh Mm Ss."""
    seconds = int(seconds)
    if seconds < 0:
        return "N/A"
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    
    if h > 0:
        return f"{h}h {m:02d}m {s:02d}s"
    elif m > 0:
        return f"{m}m {s:02d}s"
    else:
        return f"{s}s"

# ----------------------------------------------------------------------
# 0. Nombres de Archivo Dinámicos
# ----------------------------------------------------------------------

def get_best_run_filename(size):
    """Genera el nombre del archivo de las mejores partidas para un tamaño N x N."""
    return f"best_caballo_tours_{size}x{size}.txt"

def get_weights_filename(size):
    """Genera el nombre del archivo de pesos (cerebro) para un tamaño N x N."""
    return f"caballo_tour_dqn_weights_{size}x{size}.weights.h5"

def get_max_score_filename(size):
    """Genera el nombre del archivo de puntuación máxima histórica para un tamaño N x N."""
    return f"max_score_tracker_{size}x{size}.txt"

def get_total_time_filename(size):
    """Genera el nombre del archivo para el tiempo total de entrenamiento para un tamaño N x N."""
    return f"total_time_tracker_{size}x{size}.txt"

# ----------------------------------------------------------------------
# 1. FUNCIÓN DE GUARDADO PERSISTENTE (Tiempo, Score, Mejores Corridas)
# ----------------------------------------------------------------------

def load_max_score(size):
    """Carga el Max Score histórico de la IA para un tamaño específico."""
    filename = get_max_score_filename(size)
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return int(f.read().strip())
        except (ValueError, IOError) as e:
            print(f"Error al cargar {filename}: {e}. Usando valor predeterminado 0.")
    return 0

def save_max_score(score, size):
    """Guarda el nuevo Max Score histórico para un tamaño específico."""
    filename = get_max_score_filename(size)
    try:
        with open(filename, 'w') as f:
            f.write(str(score))
    except IOError as e:
        print(f"Error al guardar {filename}: {e}")

def load_total_time(size):
    """Carga el tiempo total acumulado de entrenamiento para un tamaño específico."""
    filename = get_total_time_filename(size)
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return float(f.read().strip())
        except (ValueError, IOError):
            return 0.0
    return 0.0

def save_total_time(total_seconds, size):
    """Guarda el nuevo tiempo total acumulado de entrenamiento para un tamaño específico."""
    filename = get_total_time_filename(size)
    try:
        with open(filename, 'w') as f:
            f.write(str(total_seconds))
    except IOError as e:
        print(f"Error al guardar {filename}: {e}")

def save_best_scores(best_runs, size, top_n=TOP_N_SAVES):
    """
    Guarda las top_n mejores partidas en un archivo de texto específico para el tamaño.
    """
    if not best_runs:
        return None

    best_runs.sort(key=lambda x: x['score'], reverse=True)
    filename = get_best_run_filename(size)
    
    try:
        with open(filename, 'w') as f:
            board_size = best_runs[0]['size']
            f.write(f"--- Top {top_n} Resultados del Recorrido del Caballo ({board_size}x{board_size}) ---\n")
            f.write(f"Total de casillas: {board_size * board_size}\n\n")
            
            for i, run in enumerate(best_runs[:top_n]):
                board_str = '\n'.join([' '.join(map(str, row)) for row in run['board']])
                
                f.write(f"RESULTADO #{i+1} (Score: {run['score']})\n")
                f.write(f"Posición Inicial: {run['start_pos']}\n")
                f.write(f"Tablero de Recorrido:\n")
                f.write(board_str + "\n\n")
        
        print(f"\n✅ Top {top_n} resultados guardados en {filename}")
        return filename
    except IOError as e:
        print(f"Error al escribir el archivo {filename}: {e}")
        return None

# ----------------------------------------------------------------------
# 2. FUNCIÓN PRINCIPAL DE ENTRENAMIENTO (DQN)
# ----------------------------------------------------------------------

def train_dqn(env, agent, num_episodes, board_size, callback=None, termination_flag_container=None):
    """
    Bucle principal de entrenamiento.
    """
    print(f"Iniciando entrenamiento DQN. Tablero {env.SIZE}x{env.SIZE}.")
    
    start_total_time = time.time()
    
    weights_filename = get_weights_filename(board_size)
    
    env.max_score = load_max_score(board_size)
    
    best_runs_data = []
    
    for e in range(1, num_episodes + 1):
        
        if termination_flag_container and termination_flag_container.is_terminated:
            print("\n⛔ Entrenamiento interrumpido por el usuario.")
            break 
            
        if callback:
            callback(e, num_episodes, time.time() - start_total_time)
        
        start_episode_time = time.time()
        
        start_pos = env.reset()
        done = False
        
        state = env.board / (env.SIZE * env.SIZE)
        state = np.reshape(state, (1, env.SIZE, env.SIZE, 1))

        while not done:
            valid_moves = env.get_valid_moves()
            
            if not valid_moves:
                break
                
            action_pos = agent.act(state, env.current_pos, valid_moves)
            
            if action_pos is None:
                break
            
            r, c = env.current_pos
            action_delta = (action_pos[0] - r, action_pos[1] - c)
            try:
                action_index = env.MOVE_DELTAS.index(action_delta)
            except ValueError:
                print(f"Advertencia: Acción inválida detectada en episodio {e}. Saltando.")
                break

            _, reward, done, _ = env.step(action_pos)
            
            next_state = env.board / (env.SIZE * env.SIZE)
            next_state = np.reshape(next_state, (1, env.SIZE, env.SIZE, 1))
            
            agent.memorize(state, action_index, reward, next_state, done)
            
            state = next_state
            
            agent.replay()
            
        current_score = env.step_count - 1
        
        end_episode_time = time.time()
        episode_duration = end_episode_time - start_episode_time
        
        run_data = {
            'score': current_score,
            'size': env.SIZE,
            'start_pos': start_pos,
            'board': env.board.copy()
        }
        best_runs_data.append(run_data)
        
        print(f"Episodio: {e}/{num_episodes}, Score: {current_score}, Epsilon: {agent.epsilon:.4f}, Max Score: {env.max_score}, Tiempo: {episode_duration:.2f}s")

        if e % TARGET_UPDATE_FREQ == 0:
            agent.update_target_model()
            
    end_total_time = time.time()
    total_duration = end_total_time - start_total_time
    
    print("\n" + "="*50)
    print(f"✅ ENTRENAMIENTO COMPLETADO.")
    print(f"Duración Total del Entrenamiento: {total_duration/60:.2f} minutos ({total_duration:.2f} segundos)")
    print("="*50)

    # Solo guardamos los pesos si el entrenamiento no fue interrumpido antes de terminar
    if not termination_flag_container or not termination_flag_container.is_terminated:
        
        # Acumular y guardar el tiempo total
        previous_time = load_total_time(board_size)
        new_total_time = previous_time + total_duration
        save_total_time(new_total_time, board_size)
        
        agent.save_model_weights(weights_filename)
        save_max_score(env.max_score, board_size)
            
    return save_best_scores(best_runs_data, size=board_size, top_n=TOP_N_SAVES)

# ----------------------------------------------------------------------
# 3. FUNCIONES Y CLASES DE VISUALIZACIÓN (GUI TKINTER)
# ----------------------------------------------------------------------

def generate_gradient_colors(num_colors):
    """Genera una lista de colores en degradado para cada paso del recorrido."""
    colors = []
    max_val = max(num_colors - 1, 1)
    for i in range(num_colors):
        # Va de azul (240) a rojo (0) en el espectro HSV
        hue = (240 - (i * 240 / max_val)) / 360
        saturation = 0.7
        value = 0.9
        rgb = colorsys.hsv_to_rgb(hue, saturation, value)
        hex_color = '#%02x%02x%02x' % (int(rgb[0]*255), int(rgb[1]*255), int(rgb[2]*255))
        colors.append(hex_color)
    return colors

class TourAnimator:
    """Clase para gestionar la visualización paso a paso del recorrido."""
    
    def __init__(self, board, size, path, score, root_menu_callback):
        self.board = board
        self.size = size
        self.max_score = score
        self.path = self._reconstruct_path()
        self.current_step = 1
        self.is_playing = False
        self.root_menu_callback = root_menu_callback
        
        self.gradient_colors = generate_gradient_colors(self.max_score)
        
        self.speed_map = { "1x": 200, "2x": 100, "4x": 50, "8x": 25 }
        self.delay_ms = self.speed_map["1x"]
        
        self._setup_gui()
        self.draw_board()
        
    def _reconstruct_path(self):
        """Reconstruye el path ordenado desde el board numerado."""
        path = [None] * (self.max_score + 1)
        for r in range(self.size):
            for c in range(self.size):
                val = self.board[r, c]
                if val > 0 and val <= self.max_score:
                    path[int(val)] = (r, c)
        return path
    
    def _setup_gui(self):
        self.root = tk.Tk()
        self.root.title(f"🏇 Recorrido del Caballo ({self.size}x{self.size})")
        self.root.configure(bg='#1a1a2e')
        
        style = ttk.Style()
        style.theme_use('clam')
        
        # Ajuste dinámico de CELL_SIZE (mejorado)
        if self.size <= 10:
            self.CELL_SIZE = 40
        elif self.size <= 15:
            self.CELL_SIZE = 25
        elif self.size <= 20:
            self.CELL_SIZE = 20
        elif self.size <= 30:
            self.CELL_SIZE = 15
        elif self.size <= 40:
            self.CELL_SIZE = 12
        else:
            self.CELL_SIZE = 10
        
        main_frame = tk.Frame(self.root, bg='#1a1a2e', padx=20, pady=20)
        main_frame.pack()

        title_frame = tk.Frame(main_frame, bg='#1a1a2e')
        title_frame.pack(pady=(0, 15))
        
        title_label = tk.Label(title_frame, 
                              text=f"🏆 Mejor Recorrido",
                              font=("Segoe UI", 18, "bold"),
                              fg='#00d4ff',
                              bg='#1a1a2e')
        title_label.pack()
        
        score_label = tk.Label(title_frame,
                              text=f"Score: {self.max_score}/{self.size * self.size}",
                              font=("Segoe UI", 12),
                              fg='#ffd700',
                              bg='#1a1a2e')
        score_label.pack()

        control_frame = tk.Frame(main_frame, bg='#16213e', relief=tk.RAISED, bd=2)
        control_frame.pack(pady=15, padx=10, fill=tk.X)

        buttons_frame = tk.Frame(control_frame, bg='#16213e')
        buttons_frame.pack(pady=10)
        
        self.play_button = tk.Button(buttons_frame, 
                                     text="▶️ Play", 
                                     command=self.toggle_play,
                                     font=("Segoe UI", 10, "bold"),
                                     bg='#00d4ff',
                                     fg='white',
                                     activebackground='#0096c7',
                                     relief=tk.FLAT,
                                     padx=20,
                                     pady=8,
                                     cursor='hand2')
        self.play_button.pack(side=tk.LEFT, padx=5)
        
        reset_button = tk.Button(buttons_frame, 
                                text="⏮ Reset", 
                                command=self.reset_tour,
                                font=("Segoe UI", 10, "bold"),
                                bg='#ff6b6b',
                                fg='white',
                                activebackground='#cc5555',
                                relief=tk.FLAT,
                                padx=20,
                                pady=8,
                                cursor='hand2')
        reset_button.pack(side=tk.LEFT, padx=5)

        speed_frame = tk.Frame(control_frame, bg='#16213e')
        speed_frame.pack(pady=5)
        
        tk.Label(speed_frame, 
                text="⚡ Velocidad:",
                font=("Segoe UI", 10),
                fg='white',
                bg='#16213e').pack(side=tk.LEFT, padx=10)
        
        self.speed_var = tk.StringVar(self.root)
        self.speed_var.set("1x")
        
        speeds = list(self.speed_map.keys())
        speed_menu = ttk.Combobox(speed_frame, 
                                 textvariable=self.speed_var,
                                 values=speeds,
                                 state='readonly',
                                 width=8)
        speed_menu.pack(side=tk.LEFT, padx=5)
        speed_menu.bind('<<ComboboxSelected>>', lambda e: self.set_speed(self.speed_var.get()))
        
        home_button = tk.Button(control_frame, 
                               text="🏠 Volver al Menú", 
                               command=self.back_to_menu,
                               font=("Segoe UI", 10, "bold"),
                               bg='#ffd700',
                               fg='#1a1a2e',
                               activebackground='#ffed4e',
                               relief=tk.FLAT,
                               padx=20,
                               pady=8,
                               cursor='hand2')
        home_button.pack(pady=10)

        self.status_label = tk.Label(main_frame, 
                                     text=f"Paso: 1/{self.max_score}",
                                     font=("Segoe UI", 12, "bold"),
                                     fg='#00ff88',
                                     bg='#1a1a2e')
        self.status_label.pack(pady=10)

        canvas_frame = tk.Frame(main_frame, bg='#0f3460', relief=tk.RIDGE, bd=3)
        canvas_frame.pack()
        
        self.canvas = tk.Canvas(canvas_frame, 
                                width=self.size * self.CELL_SIZE, 
                                height=self.size * self.CELL_SIZE, 
                                bg="#0f3460",
                                highlightthickness=0)
        self.canvas.pack(padx=5, pady=5)
        
        self.root.protocol("WM_DELETE_WINDOW", self.back_to_menu)
        
        configure_window(self.root, 
                         width=self.size * self.CELL_SIZE + 100, 
                         height=self.size * self.CELL_SIZE + 200, 
                         resizable=True)
        
    def back_to_menu(self):
        self.root.destroy()
        self.root_menu_callback()

    def set_speed(self, speed):
        self.delay_ms = self.speed_map.get(speed, 200)

    def reset_tour(self):
        self.current_step = 1
        self.is_playing = False
        self.play_button.config(text="▶️ Play", bg='#00d4ff')
        self.draw_board()
        self.status_label.config(text=f"Paso: 1/{self.max_score}")

    def toggle_play(self):
        self.is_playing = not self.is_playing
        if self.is_playing:
            self.play_button.config(text="⏸ Pausa", bg='#ff6b6b')
            self.animate_step()
        else:
            self.play_button.config(text="▶️ Play", bg='#00d4ff')

    def animate_step(self):
        if not self.is_playing or self.current_step > self.max_score:
            if self.current_step > self.max_score:
                self.is_playing = False
                self.play_button.config(text="✓ Terminado", bg='#00ff88')
            return

        self.draw_board(steps_to_show=self.current_step)
        
        self.status_label.config(text=f"Paso: {self.current_step}/{self.max_score}")

        self.current_step += 1
        
        if self.is_playing:
            self.root.after(self.delay_ms, self.animate_step)

    def draw_board(self, steps_to_show=1):
        self.canvas.delete("all")
        
        COLOR_BG = "#1a1a2e"
        
        # 1. Dibujar líneas de camino
        for i in range(1, steps_to_show):
            if i < len(self.path) and (i + 1) < len(self.path):
                r1, c1 = self.path[i]
                r2, c2 = self.path[i+1]
                x1 = c1 * self.CELL_SIZE + self.CELL_SIZE / 2
                y1 = r1 * self.CELL_SIZE + self.CELL_SIZE / 2
                x2 = c2 * self.CELL_SIZE + self.CELL_SIZE / 2
                y2 = r2 * self.CELL_SIZE + self.CELL_SIZE / 2
                # Dibuja la línea de movimiento
                self.canvas.create_line(x1, y1, x2, y2, fill="#ffd700", width=2, arrow=tk.LAST)
        
        # 2. Dibujar celdas y números
        for r in range(self.size):
            for c in range(self.size):
                x1, y1 = c * self.CELL_SIZE, r * self.CELL_SIZE
                x2, y2 = x1 + self.CELL_SIZE, y1 + self.CELL_SIZE
                
                value = self.board[r, c]
                
                if 0 < value <= steps_to_show:
                    fill_color = self.gradient_colors[int(value) - 1]
                    
                    show_number = self.CELL_SIZE > 15
                    
                    if show_number:
                        font_size = 12 if self.size <= 10 else 9 if self.size <= 15 else 7
                    
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                fill=fill_color, 
                                                outline="#ffffff",
                                                width=2)
                    
                    if show_number:
                        # Sombra para mejor legibilidad
                        self.canvas.create_text(x1 + self.CELL_SIZE / 2 + 1, 
                                              y1 + self.CELL_SIZE / 2 + 1, 
                                              text=str(value), 
                                              fill="black", 
                                              font=("Segoe UI", font_size, "bold"))
                        
                        self.canvas.create_text(x1 + self.CELL_SIZE / 2, 
                                              y1 + self.CELL_SIZE / 2, 
                                              text=str(value), 
                                              fill="white", 
                                              font=("Segoe UI", font_size, "bold"))
                else:
                    self.canvas.create_rectangle(x1, y1, x2, y2, 
                                                fill=COLOR_BG, 
                                                outline="#333",
                                                width=1)
        
        # 3. Icono de caballo en la posición actual
        if steps_to_show > 0 and steps_to_show < len(self.path) and self.path[steps_to_show]:
            r, c = self.path[steps_to_show]
            x = c * self.CELL_SIZE + self.CELL_SIZE / 2
            y = r * self.CELL_SIZE + self.CELL_SIZE / 2
            # El icono debe verse bien, ajustamos la posición para el centro de la celda
            self.canvas.create_text(x, y, text="🏇", font=("Segoe UI", int(self.CELL_SIZE * 0.7)), fill="#ff0000")


def extract_best_run(filename):
    """
    Lee el archivo TXT para extraer el mejor tablero, el score, y el camino ordenado.
    """
    if not os.path.exists(filename):
        return None, None, None, None

    try:
        with open(filename, 'r') as f:
            content = f.read()
    except IOError as e:
        print(f"Error al leer {filename}: {e}")
        return None, None, None, None

    # Buscar el primer resultado (RESULTADO #1)
    score_match = [line for line in content.split('\n') if line.startswith('RESULTADO #1 (Score: ')]
    if not score_match:
        return None, None, None, None
        
    try:
        max_score = int(score_match[0].split('(Score: ')[1].split(')')[0])
    except:
        max_score = 0

    start_tag = "Tablero de Recorrido:\n"
    end_tag = "\n\nRESULTADO #2"
    
    start_index = content.find(start_tag) + len(start_tag)
    end_index = content.find(end_tag)
    
    board_str_block = content[start_index:end_index].strip() if end_index != -1 else content[start_index:].strip()

    if not board_str_block:
        return None, None, None, None

    try:
        # Asegurarse de que no lee la línea en blanco al final
        board_list = [list(map(int, line.split())) for line in board_str_block.split('\n') if line.strip()]
        board_array = np.array(board_list)
        size = board_array.shape[0]
        
        # Si el score extraído no coincide con el máximo en el tablero, usamos el del tablero
        if max_score != np.amax(board_array):
             max_score = np.amax(board_array)
             
        path = [None] * (max_score + 1)
        
        return board_array, size, path, max_score

    except Exception as e:
        print(f"Error al parsear el tablero en {filename}: {e}")
        return None, None, None, None

def display_top_run_animated(filename, size):
    """Función principal para iniciar la animación del mejor recorrido para un tamaño específico."""
    
    if size > 30:
        messagebox.showwarning("Advertencia de Tamaño", 
                               f"El tablero es demasiado grande ({size}x{size}). La animación puede ser muy lenta. Máximo recomendado: 30x30.")
    
    board, size_read, path, score = extract_best_run(filename)
    
    root_menu_callback = main_menu
    
    if board is not None and size_read == size:
        print(f"\n✨ Visualizando la animación del Mejor Recorrido ({size}x{size}) - Score: {score}...")
        animator = TourAnimator(board, size, path, score, root_menu_callback)
        animator.root.mainloop()
    else:
        messagebox.showinfo("Información", f"No se encontraron datos de la mejor partida guardada para el tablero {size}x{size}. ¡Debes entrenar primero en ese tamaño!")
        root_menu_callback()
        
# ----------------------------------------------------------------------
# CLASE PARA LA VENTANA DE REGISTRO DE TIEMPOS
# ----------------------------------------------------------------------
class TimeLogWindow:
    """Clase para gestionar la ventana de registro de tiempos acumulados."""
    def __init__(self, root_menu, allowed_sizes):
        self.root_menu = root_menu
        self.allowed_sizes = allowed_sizes
        
        self.window = tk.Toplevel(self.root_menu)
        self.window.title("⏱️ Registro de Tiempos de Entrenamiento")
        self.window.configure(bg='#1a1a2e')
        self.window.grab_set()
        self.window.focus_set()
        
        # Configuración de tamaño para la ventana de registro
        configure_window(self.window, width=500, height=450)
        
        main_frame = tk.Frame(self.window, bg='#1a1a2e', padx=20, pady=20)
        main_frame.pack(expand=True, fill=tk.BOTH)
        
        tk.Label(main_frame,
               text="⏱️ Tiempos de Entrenamiento Acumulados",
               font=("Segoe UI", 16, "bold"),
               fg='#00ff88',
               bg='#1a1a2e').pack(pady=10)

        # Configurar Treeview
        columns = ("#1", "#2")
        # Altura dinámica basada en la lista de tamaños
        tree_height = min(len(allowed_sizes), 15)
        tree = ttk.Treeview(main_frame, columns=columns, show='headings', height=tree_height)
        
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Segoe UI', 10, 'bold'), background="#16213e", foreground="white")
        style.configure("Treeview", font=('Segoe UI', 10), background="#1a1a2e", foreground="#cccccc")
        style.map('Treeview', background=[('selected', '#00d4ff')], foreground=[('selected', 'black')])

        tree.heading("#1", text="Tablero (N x N)", anchor=tk.W)
        tree.heading("#2", text="Tiempo Total", anchor=tk.W)
        tree.column("#1", width=120, anchor=tk.W)
        tree.column("#2", width=250, anchor=tk.W)
        
        self._load_data(tree)
        
        tree.pack(pady=10, padx=5, fill=tk.BOTH, expand=True)

        # Botón para volver al menú
        tk.Button(main_frame,
                  text="🏠 Volver al Menú Principal",
                  command=self.back_to_menu,
                  font=("Segoe UI", 11, "bold"),
                  bg='#ff6b6b',
                  fg='white',
                  activebackground='#cc5555',
                  relief=tk.FLAT,
                  padx=20,
                  pady=10,
                  cursor='hand2').pack(pady=20)
                  
        self.window.protocol("WM_DELETE_WINDOW", self.back_to_menu)

    def _load_data(self, tree):
        for size_str in self.allowed_sizes:
            size = int(size_str)
            total_time_seconds = load_total_time(size)
            formatted_time = format_time(total_time_seconds)
            
            tree.insert('', tk.END, values=(f"{size}x{size}", formatted_time))

    def back_to_menu(self):
        self.window.destroy()
        self.root_menu.deiconify() # Muestra de nuevo la ventana principal


# ----------------------------------------------------------------------
# 4. BLOQUE PRINCIPAL DE EJECUCIÓN CON MENÚ, TEMPORIZADOR Y THREADING
# ----------------------------------------------------------------------

class TrainingConfirmationWindow:
    """Clase para la ventana de confirmación previa, progreso y temporizador de espera."""
    
    def __init__(self, root_menu, board_size, num_episodes):
        self.root_menu = root_menu
        self.board_size = board_size
        self.num_episodes = num_episodes
        self.max_score = load_max_score(board_size)
        self.training_thread = None
        self.start_time = None

        self.is_terminated = False 

        self.stable_avg_time_per_episode = 0.0
        self.last_stable_update_time = -STABLE_UPDATE_INTERVAL
        self.last_stable_update_episode = 0
        
        self._setup_gui()
        self._display_info()
        
    def _setup_gui(self):
        self.window = tk.Toplevel(self.root_menu)
        self.window.title("⚠️ Confirmar Entrenamiento DQN")
        self.window.configure(bg='#1a1a2e')
        self.window.grab_set()
        self.window.focus_set()
        
        configure_window(self.window)
        
        self.main_frame = tk.Frame(self.window, bg='#1a1a2e', padx=20, pady=10)
        self.main_frame.pack()
        
        self.title_label = tk.Label(self.main_frame,
                                     text="¡ATENCIÓN! El Entrenamiento va a Comenzar",
                                     font=("Segoe UI", 14, "bold"),
                                     fg='#ff6b6b',
                                     bg='#1a1a2e',
                                     pady=10)
        self.title_label.pack()

        self.info_frame = tk.Frame(self.main_frame, bg='#16213e', padx=15, pady=15, relief=tk.FLAT, bd=1)
        self.info_frame.pack(pady=10)
        
        self.button_frame = tk.Frame(self.main_frame, bg='#1a1a2e', pady=10)
        self.button_frame.pack(pady=(0, 15))
        
    def _display_info(self):
        
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        
        tk.Label(self.info_frame, 
                 text=f"Tamaño del Tablero: {self.board_size}x{self.board_size} (Total: {self.board_size*self.board_size} casillas)",
                 font=("Segoe UI", 11),
                 fg='#00d4ff',
                 bg='#16213e',
                 anchor='w').pack(fill=tk.X)
                 
        tk.Label(self.info_frame, 
                 text=f"Fases (Episodios) a Ejecutar: {self.num_episodes}",
                 font=("Segoe UI", 11),
                 fg='white',
                 bg='#16213e',
                 anchor='w').pack(fill=tk.X)
                 
        tk.Label(self.info_frame, 
                 text=f"Récord Actual ({self.board_size}x{self.board_size}): {self.max_score}",
                 font=("Segoe UI", 11, "bold"),
                 fg='#ffd700',
                 bg='#16213e',
                 anchor='w').pack(fill=tk.X, pady=(5, 0))

        warning_text = "Advertencia: El entrenamiento con Deep Q-Learning puede tardar varios minutos u horas..."
        tk.Label(self.main_frame,
                 text=warning_text,
                 font=("Segoe UI", 9, "italic"),
                 fg='#8888ff',
                 bg='#1a1a2e',
                 wraplength=350,
                 pady=10).pack(padx=20)
                 
        for widget in self.button_frame.winfo_children():
            widget.destroy()

        tk.Button(self.button_frame,
                  text="✅ COMENZAR AHORA",
                  command=self.start_training_flow,
                  font=("Segoe UI", 11, "bold"),
                  bg='#00ff88',
                  fg='#1a1a2e',
                  activebackground='#00cc6f',
                  relief=tk.FLAT,
                  padx=20,
                  pady=10,
                  cursor='hand2').pack(side=tk.LEFT, padx=10)
                  
        tk.Button(self.button_frame,
                  text="❌ CANCELAR Y VOLVER",
                  command=self.window.destroy,
                  font=("Segoe UI", 11),
                  bg='#ff6b6b',
                  fg='white',
                  activebackground='#cc5555',
                  relief=tk.FLAT,
                  padx=20,
                  pady=10,
                  cursor='hand2').pack(side=tk.LEFT, padx=10)


    def _display_waiting(self):
        self.window.title("⏳ Entrenamiento en Curso...")
        
        self.title_label.config(text="🔥 ENTRENAMIENTO DQN EN CURSO", fg='#00d4ff')
        for widget in self.info_frame.winfo_children():
            widget.destroy()
        for widget in self.button_frame.winfo_children():
            widget.destroy()
            
        self.progress_label = tk.Label(self.info_frame, 
                                        text="Estado: Inicializando...",
                                        font=("Segoe UI", 12),
                                        fg='white',
                                        bg='#16213e',
                                        anchor='w')
        self.progress_label.pack(fill=tk.X, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(self.info_frame, orient='horizontal', length=300, mode='determinate')
        self.progress_bar.pack(pady=5)
        
        self.timer_label = tk.Label(self.info_frame, 
                                    text="Tiempo Transcurrido: 0s",
                                    font=("Segoe UI", 12, "bold"),
                                    fg='#ffd700',
                                    bg='#16213e',
                                    anchor='w')
        self.timer_label.pack(fill=tk.X, pady=(5, 0))
        
        tk.Button(self.button_frame,
                  text="Volver al Menú (Detención Controlada)",
                  command=self.terminate_training,
                  font=("Segoe UI", 11),
                  bg='#ff6b6b',
                  fg='white',
                  activebackground='#cc5555',
                  relief=tk.FLAT,
                  padx=20,
                  pady=10,
                  cursor='hand2').pack(padx=10)


    def start_training_flow(self):
        self.root_menu.withdraw()
        
        self._display_waiting()
        
        self.start_time = time.time()
        self.update_timer_and_progress(0, self.num_episodes, 0)
        
        self.training_thread = threading.Thread(target=self._run_training_target)
        self.training_thread.start()


    def _run_training_target(self):
        """Función objetivo para el hilo de entrenamiento."""
        try:
            saved_filename = run_dqn_process(self.board_size, self.num_episodes, self._update_progress_callback, self)
            
            self.window.after(0, self.training_completed, saved_filename)
            
        except Exception as e:
            print(f"Error fatal durante el entrenamiento: {e}")
            self.window.after(0, lambda: messagebox.showerror("Error", f"Ocurrió un error grave durante el entrenamiento: {e}"))
            self.window.after(0, self.training_completed, None)


    def _update_progress_callback(self, current_episode, total_episodes, elapsed_time):
        progress_text = f"Episodio: {current_episode}/{total_episodes} ({current_episode*100/total_episodes:.2f}%)"
        
        if self.window.winfo_exists():
            self.window.after(0, lambda: self.progress_label.config(text=progress_text))
            
            progress_value = (current_episode / total_episodes) * 100
            self.window.after(0, lambda: self.progress_bar.config(value=progress_value))
            
            self.window.after(0, lambda: self.update_timer_and_progress(current_episode, total_episodes, elapsed_time))

    def update_timer_and_progress(self, current_episode, total_episodes, elapsed_time):
        if not self.window.winfo_exists(): return
        if self.start_time is None: return 
        
        elapsed = time.time() - self.start_time
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        
        timer_text = f"Tiempo Transcurrido: {minutes:02d}m {seconds:02d}s"

        est_text = ""
        
        if current_episode > 0:
            if elapsed - self.last_stable_update_time >= STABLE_UPDATE_INTERVAL:
                self.stable_avg_time_per_episode = elapsed / current_episode
                self.last_stable_update_time = elapsed
                self.last_stable_update_episode = current_episode 

            if self.stable_avg_time_per_episode > 0:
                avg_time_per_episode = self.stable_avg_time_per_episode
                remaining_episodes = total_episodes - current_episode
                
                estimated_remaining_time = avg_time_per_episode * remaining_episodes
                
                if estimated_remaining_time < 3600 * 4: 
                    rem_h = int(estimated_remaining_time // 3600)
                    rem_m = int((estimated_remaining_time % 3600) // 60)
                    rem_s = int(estimated_remaining_time % 60)
                    
                    if rem_h > 0:
                        est_text = f" | Est. Restante: {rem_h}h {rem_m:02d}m"
                    elif rem_m > 0:
                        est_text = f" | Est. Restante: {rem_m:02d}m {rem_s:02d}s"
                    else:
                        est_text = f" | Est. Restante: {rem_s:02d}s"
                else:
                    est_text = " | Est. Restante: >4h (Entrenamiento muy largo)"
             
        self.timer_label.config(text=timer_text + est_text)

        if self.training_thread and self.training_thread.is_alive() and self.window.winfo_exists():
            self.window.after(1000, lambda: self.update_timer_and_progress(current_episode, total_episodes, elapsed_time))


    def training_completed(self, saved_filename):
        """Se llama cuando el hilo de entrenamiento ha terminado (sea normal o interrumpido)."""
        if self.root_menu and not self.root_menu.winfo_exists():
            self.root_menu.deiconify()
             
        self.window.destroy()

    def terminate_training(self):
        """CRÍTICO: Intenta terminar el proceso de entrenamiento de forma segura."""
        if self.training_thread and self.training_thread.is_alive():
            self.is_terminated = True
            messagebox.showwarning("Advertencia", "Señal de detención enviada. El entrenamiento finalizará de forma segura al terminar el episodio actual.")
        else:
            self.window.destroy()
            main_menu()

def run_dqn_process(board_size, num_episodes, callback, window_instance):
    """Función que maneja la inicialización real del agente y el entrenamiento."""
    env = CaballoTourEnvironment(size=board_size)
    state_shape = (board_size, board_size)
    action_count = 8
    agent = DQNAgent(state_shape, action_count, board_size, env.MOVE_DELTAS)

    weights_filename = get_weights_filename(board_size)
    agent.load_model_weights(weights_filename)
    
    saved_filename = train_dqn(env, agent, 
                               num_episodes=num_episodes, 
                               board_size=board_size, 
                               callback=callback,
                               termination_flag_container=window_instance)
    
    if saved_filename and not window_instance.is_terminated:
        display_top_run_animated(saved_filename, board_size)
    else:
        main_menu() 
        
    return saved_filename

def get_episodes_and_run(root_menu, board_size):
    num_episodes_str = simpledialog.askstring("Entrenamiento DQN", f"¿Cuántas fases (episodios) deseas ejecutar para el tablero {board_size}x{board_size}? (e.g., 50, 5000)", parent=root_menu)
    
    try:
        num_episodes = int(num_episodes_str)
        if num_episodes <= 0: raise ValueError
    except ValueError:
        messagebox.showerror("Error de entrada", "Por favor, introduce un número entero positivo válido.")
        return
    
    TrainingConfirmationWindow(root_menu, board_size, num_episodes)

def show_time_log(root_menu, allowed_sizes):
    """Oculta el menú principal y abre la ventana de registro de tiempos."""
    root_menu.withdraw() 
    TimeLogWindow(root_menu, allowed_sizes)

def main_menu():
    root_menu = tk.Tk()
    root_menu.title("🏇 Caballo Tour - Sistema de IA")
    root_menu.configure(bg='#0f0f1e')
    
    configure_window(root_menu)
    
    style = ttk.Style()
    style.theme_use('clam')
    
    main_frame = tk.Frame(root_menu, bg='#0f0f1e', padx=40, pady=15)
    main_frame.pack()
    
    title_label = tk.Label(main_frame,
                          text="🏇 CABALLO TOUR",
                          font=("Segoe UI", 24, "bold"),
                          fg='#00d4ff',
                          bg='#0f0f1e')
    title_label.pack(pady=(0, 5))
    
    subtitle_label = tk.Label(main_frame,
                             text="Sistema de Aprendizaje por Refuerzo",
                             font=("Segoe UI", 12),
                             fg='#8888ff',
                             bg='#0f0f1e')
    subtitle_label.pack(pady=(0, 20))
    
    # Lista de tamaños para el menú (igual que en la sección de configuración)
    allowed_sizes = [str(s) for s in range(10, 101, 10)]
    
    # CONFIGURACIÓN
    config_frame = tk.Frame(main_frame, bg='#1a1a2e', relief=tk.RAISED, bd=2)
    config_frame.pack(pady=10, padx=20, fill=tk.X)
    
    config_title = tk.Label(config_frame,
                           text="⚙️ Configuración",
                           font=("Segoe UI", 14, "bold"),
                           fg='#ffd700',
                           bg='#1a1a2e')
    config_title.pack(pady=10)
    
    size_frame = tk.Frame(config_frame, bg='#1a1a2e')
    size_frame.pack(pady=10)
    
    tk.Label(size_frame,
            text="Tamaño del Tablero (N x N):",
            font=("Segoe UI", 11),
            fg='white',
            bg='#1a1a2e').pack(side=tk.LEFT, padx=10)
    
    board_size_var = tk.StringVar(root_menu)
    board_size_var.set(allowed_sizes[0])
    
    size_combo = ttk.Combobox(size_frame,
                             textvariable=board_size_var,
                             values=allowed_sizes,
                             state='readonly',
                             width=10,
                             font=("Segoe UI", 11))
    size_combo.pack(side=tk.LEFT, padx=10)
    
    # BOTONES
    buttons_frame = tk.Frame(main_frame, bg='#0f0f1e')
    buttons_frame.pack(pady=20)
    
    def start_training_flow():
        selected_size = int(board_size_var.get())
        root_menu.withdraw() 
        get_episodes_and_run(root_menu, selected_size)

    def start_viewing_flow():
        selected_size = int(board_size_var.get())
        filename = get_best_run_filename(selected_size)
        root_menu.destroy()
        display_top_run_animated(filename, selected_size)

    train_button = tk.Button(buttons_frame,
                            text="🧠 INICIAR ENTRENAMIENTO",
                            command=start_training_flow,
                            font=("Segoe UI", 12, "bold"),
                            bg='#00d4ff',
                            fg='white',
                            activebackground='#0096c7',
                            relief=tk.FLAT,
                            padx=30,
                            pady=15,
                            cursor='hand2')
    train_button.pack(pady=8, fill=tk.X)
    
    # 🌟 NUEVO BOTÓN PARA EL REGISTRO DE TIEMPOS
    time_log_button = tk.Button(buttons_frame,
                           text="⏱️ VER REGISTRO DE TIEMPOS",
                           command=lambda: show_time_log(root_menu, allowed_sizes),
                           font=("Segoe UI", 12, "bold"),
                           bg='#ffd700',
                           fg='#0f0f1e',
                           activebackground='#ffed4e',
                           relief=tk.FLAT,
                           padx=30,
                           pady=15,
                           cursor='hand2')
    time_log_button.pack(pady=8, fill=tk.X)
    
    view_button = tk.Button(buttons_frame,
                           text="🖼️ VER MEJOR RECORRIDO",
                           command=start_viewing_flow,
                           font=("Segoe UI", 12, "bold"),
                           bg='#00ff88',
                           fg='#0f0f1e',
                           activebackground='#00cc6f',
                           relief=tk.FLAT,
                           padx=30,
                           pady=15,
                           cursor='hand2')
    view_button.pack(pady=8, fill=tk.X)
    
    exit_button = tk.Button(buttons_frame,
                           text="❌ SALIR",
                           command=root_menu.destroy,
                           font=("Segoe UI", 10),
                           bg='#ff6b6b',
                           fg='white',
                           activebackground='#cc5555',
                           relief=tk.FLAT,
                           padx=30,
                           pady=10,
                           cursor='hand2')
    exit_button.pack(pady=(15, 0), fill=tk.X)
    
    footer_label = tk.Label(main_frame,
                           text="Powered by Deep Q-Learning Neural Network",
                           font=("Segoe UI", 8),
                           fg='#666',
                           bg='#0f0f1e')
    footer_label.pack(pady=(10, 0))
    
    root_menu.mainloop()


if __name__ == "__main__":
    main_menu()