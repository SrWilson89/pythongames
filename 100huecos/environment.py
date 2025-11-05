# environment.py

import numpy as np
import random
import time

class CaballoTourEnvironment:
    """
    Representa el tablero de 100x100 para el recorrido del caballo y gestiona la lógica del juego.
    """
    
    def __init__(self, size=100):
        """Inicializa el tablero y los parámetros del juego."""
        self.SIZE = size
        # Las 8 posibles movimientos del caballo (delta_fila, delta_columna)
        self.MOVE_DELTAS = [
            (2, 1), (2, -1), (-2, 1), (-2, -1),
            (1, 2), (1, -2), (-1, 2), (-1, -2)
        ]
        self.max_score = 0
        self.reset()

    def reset(self):
        """
        Reinicia el tablero para una nueva partida.
        Devuelve el estado inicial (la posición del caballo).
        """
        # El tablero se inicializa con 0. Los números secuenciales (1, 2, 3...) llenarán las casillas.
        self.board = np.zeros((self.SIZE, self.SIZE), dtype=int)
        
        # Elegir una posición inicial aleatoria
        start_r = random.randint(0, self.SIZE - 1)
        start_c = random.randint(0, self.SIZE - 1)
        self.current_pos = (start_r, start_c)
        
        # El juego siempre comienza con el número 1
        self.step_count = 1
        self.board[start_r, start_c] = self.step_count
        
        return self.current_pos

    def _is_valid(self, r, c):
        """Verifica si una posición está dentro de los límites del tablero."""
        return 0 <= r < self.SIZE and 0 <= c < self.SIZE

    def get_valid_moves(self, pos=None):
        """
        Calcula todos los movimientos legales (dentro de límites y a casillas vacías)
        desde una posición dada.
        """
        if pos is None:
            pos = self.current_pos
            
        r, c = pos
        valid_moves = []
        
        for dr, dc in self.MOVE_DELTAS:
            new_r, new_c = r + dr, c + dc
            
            # 1. Verificar límites
            if self._is_valid(new_r, new_c):
                # 2. Verificar si la casilla está vacía (valor 0)
                if self.board[new_r, new_c] == 0:
                    valid_moves.append((new_r, new_c))
                    
        return valid_moves

    def step(self, action):
        """
        Ejecuta un movimiento (acción) del caballo y calcula la recompensa.
        
        Args:
            action (tuple): La nueva posición (fila, columna) elegida por el agente.
            
        Returns:
            tuple: (new_state, reward, done, info)
        """
        
        # 1. Mover el caballo
        self.current_pos = action
        self.step_count += 1
        r, c = action
        
        # 2. Marcar la casilla con el nuevo número secuencial
        self.board[r, c] = self.step_count
        
        # 3. Determinar el final del juego
        next_valid_moves = self.get_valid_moves(self.current_pos)
        done = len(next_valid_moves) == 0
        
        # 4. Asignar recompensa
        # Recompensa base: +0.1 por cada paso exitoso
        reward = 0.1
        
        # Recompensa/Castigo final (si el juego terminó)
        if done:
            if self.step_count > self.max_score:
                # Gran recompensa por superar la puntuación máxima anterior
                reward += self.SIZE * self.SIZE # Recompensa proporcional al tamaño del tablero
                self.max_score = self.step_count
            else:
                # Castigo por terminar sin récord
                reward -= 10
        
        # El nuevo estado es la nueva posición del caballo
        new_state = self.current_pos
        
        info = {}
        
        return new_state, reward, done, info

# Fin de environment.py