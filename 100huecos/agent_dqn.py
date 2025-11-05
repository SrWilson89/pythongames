# agent_dqn.py

import numpy as np
import random
from collections import deque
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Flatten, Conv2D, Input
from tensorflow.keras.optimizers import Adam

class DQNAgent:
    def __init__(self, state_size, action_size, size_board, env_move_deltas):
        self.state_size = state_size
        self.action_size = action_size
        self.size_board = size_board
        self.env_move_deltas = env_move_deltas

        # Hiperparámetros de RL
        self.gamma = 0.95
        self.learning_rate = 0.001
        self.epsilon = 1.0
        self.epsilon_min = 0.01
        self.epsilon_decay = 0.99995 
        self.batch_size = 64

        # Memoria de Experiencia
        self.memory = deque(maxlen=200000) 

        # Modelos Q y Target
        self.model = self._build_model()
        self.target_model = self._build_model()
        self.update_target_model() 

    def _build_model(self):
        """Crea la red neuronal (Deep Q-Network) con capas convolucionales."""
        model = Sequential()
        
        model.add(Input(shape=(self.size_board, self.size_board, 1))) 
        
        model.add(Conv2D(32, (3, 3), activation='relu', padding='same'))
        model.add(Conv2D(64, (3, 3), activation='relu', padding='same'))
        
        model.add(Flatten()) 
        model.add(Dense(256, activation='relu'))
        model.add(Dense(self.action_size, activation='linear'))
        
        model.compile(loss='mse',
                      optimizer=Adam(learning_rate=self.learning_rate))
        return model

    def update_target_model(self):
        """Actualiza los pesos del modelo Target con los pesos del modelo Q."""
        self.target_model.set_weights(self.model.get_weights())

    # --- Métodos de Persistencia CORREGIDOS ---
    
    def save_model_weights(self, filename="caballo_tour_dqn_weights.weights.h5"):
        """Guarda los pesos del modelo Q."""
        self.model.save_weights(filename)
        print(f"🧠 Pesos del modelo guardados en: {filename}")

    def load_model_weights(self, filename="caballo_tour_dqn_weights.weights.h5"):
        """Carga los pesos del modelo Q y ajusta Epsilon."""
        try:
            self.model.load_weights(filename)
            self.update_target_model()
            
            self.epsilon = max(0.5, self.epsilon) 
            print(f"✅ Pesos del modelo cargados desde: {filename}. Epsilon inicial: {self.epsilon:.4f}")
            return True
        except Exception as e:
            return False

    def memorize(self, state, action_index, reward, next_state, done):
        """Almacena una experiencia en la memoria."""
        self.memory.append((state, action_index, reward, next_state, done))

    def act(self, state, current_pos, valid_moves):
        """Elige una acción basándose en la estrategia epsilon-greedy."""
        if not valid_moves:
            return None 

        if np.random.rand() <= self.epsilon:
            return random.choice(valid_moves)

        q_values = self.model.predict(state, verbose=0)[0]
        
        best_q = -np.inf
        best_action_index = -1
        
        r, c = current_pos
        
        for i, move_delta in enumerate(self.env_move_deltas):
            next_pos = (r + move_delta[0], c + move_delta[1])
            
            if next_pos in valid_moves and q_values[i] > best_q:
                best_q = q_values[i]
                best_action_index = i
        
        if best_action_index != -1:
            dr, dc = self.env_move_deltas[best_action_index]
            return (r + dr, c + dc)
        else:
            return random.choice(valid_moves)
            
    def replay(self):
        """Entrena el modelo Q en un lote de experiencias muestreadas."""
        if len(self.memory) < self.batch_size:
            return

        minibatch = random.sample(self.memory, self.batch_size)
        
        states = np.array([m[0][0] for m in minibatch])
        next_states = np.array([m[3][0] for m in minibatch])
        
        target_q = self.target_model.predict(next_states, verbose=0)
        target_f = self.model.predict(states, verbose=0)
        
        for i, (state, action_index, reward, next_state, done) in enumerate(minibatch):
            target = reward
            if not done:
                target = (reward + self.gamma * np.amax(target_q[i]))
            
            target_f[i][action_index] = target
            
        self.model.fit(states, target_f, epochs=1, verbose=0)
        
        if self.epsilon > self.epsilon_min:
            self.epsilon *= self.epsilon_decay