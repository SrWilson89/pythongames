import time
from tkinter import Tk, Label, Entry, Button, END, messagebox, LEFT, X
from tkinter.ttk import Style

# --- CONFIGURACIÓN DE SONIDO (Solo funciona en Windows) ---
try:
    import winsound
    
    # 1. Ajuste de Velocidad: La variable UNIT_TIME controla el ritmo.
    # 0.15 segundos es una velocidad media, clara y reconocible.
    UNIT_TIME = 0.15 
    
    # Reglas de tiempo basadas en UNIT_TIME (T)
    FREQ = 600
    DOT_DURATION = int(UNIT_TIME * 1000)      # Punto = 1T (en ms)
    DASH_DURATION = int(UNIT_TIME * 3 * 1000) # Guion = 3T (en ms)
    ELEMENT_PAUSE = UNIT_TIME                 # Pausa entre símbolos = 1T (en segundos)
    WORD_PAUSE = UNIT_TIME * 7                # Pausa entre palabras = 7T (en segundos)

    def play_morse(morse_code, morse_label):
        morse_label.config(text="Reproduciendo...")
        root.update() 

        for char in morse_code:
            if char == '.':
                current_text = morse_label.cget("text")
                morse_label.config(text=current_text + ".")
                root.update() 
                winsound.Beep(FREQ, DOT_DURATION)
                time.sleep(ELEMENT_PAUSE) # Pausa de 1T
            elif char == '-':
                current_text = morse_label.cget("text")
                morse_label.config(text=current_text + "-")
                root.update()
                winsound.Beep(FREQ, DASH_DURATION)
                time.sleep(ELEMENT_PAUSE) # Pausa de 1T
            elif char == '/': 
                current_text = morse_label.cget("text")
                morse_label.config(text=current_text + " / ")
                root.update()
                time.sleep(WORD_PAUSE) # Pausa de 7T
            
            # Pausa extra entre símbolos (siempre debe haber una pausa de 1T entre puntos/guiones)
            if char in '.-':
                time.sleep(ELEMENT_PAUSE)
        
        morse_label.config(text=morse_code) # Muestra el código completo al finalizar

except ImportError:
    # Función de respaldo si winsound no está disponible (Linux/macOS)
    def play_morse(morse_code, morse_label):
        messagebox.showwarning("Advertencia", "El sonido solo funciona en Windows o requiere librerías adicionales (pyaudio/simpleaudio) que no están instaladas.")
        morse_label.config(text=f"Sonido NO disponible. Código: {morse_code}")

# --- DICCIONARIO DE CÓDIGO MORSE ---
MORSE_CODE_DICT = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..', 'E': '.', 'F': '..-.', 
    'G': '--.', 'H': '....', 'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..', 
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.', 'Q': '--.-', 'R': '.-.', 
    'S': '...', 'T': '-', 'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-', 
    'Y': '-.--', 'Z': '--..',
    '1': '.----', '2': '..---', '3': '...--', '4': '....-', '5': '.....', 
    '6': '-....', '7': '--...', '8': '---..', '9': '----.', '0': '-----',
    ' ': '/' # Usamos '/' como separador de palabras en la lógica Morse
}

# --- LÓGICA DE TRADUCCIÓN ---
def encrypt_to_morse(message):
    cipher = ''
    for letter in message.upper():
        if letter in MORSE_CODE_DICT:
            # Agrega el código y un espacio para separar las letras dentro de una palabra
            cipher += MORSE_CODE_DICT[letter] + ' '
        elif letter == ' ':
            # Agrega el separador de palabras ('/')
            cipher += MORSE_CODE_DICT[letter] + ' '
    return cipher.strip()

# --- FUNCIONES DE LA INTERFAZ ---

def translate_and_display():
    """Traduce el texto y muestra el código Morse."""
    message = input_entry.get()
    if not message.strip():
        morse_display_label.config(text="---")
        return

    # Traduce
    morse_translated = encrypt_to_morse(message)

    # Actualiza la etiqueta de visualización
    morse_display_label.config(text=morse_translated)
    
    # Guarda el código traducido para el botón de reproducción
    global current_morse_code
    current_morse_code = morse_translated

def play_current_morse():
    """Reproduce el último código Morse traducido."""
    global current_morse_code
    
    if not current_morse_code:
        messagebox.showerror("Error", "Primero traduce un mensaje en el campo de texto.")
        return
    
    # Inicia la reproducción y visualización en tiempo real
    play_morse(current_morse_code, morse_display_label)


# --- VENTANA PRINCIPAL (TKINTER) ---

# Variable global para almacenar el último código traducido
current_morse_code = ""

root = Tk()
root.title("Traductor de Texto a Código Morse")
root.geometry("600x320")
root.resizable(False, False)

# Estilo y fuente
style = Style()
style.configure("TButton", font=('Arial', 10), padding=10)

# 1. Entrada de Texto
Label(root, text="Escribe tu mensaje:", font=('Arial', 12)).pack(pady=10)
input_entry = Entry(root, width=50, font=('Arial', 14))
input_entry.pack(pady=5)
# Vincula la función de traducción a la tecla Enter
input_entry.bind('<Return>', lambda event: translate_and_display())


# 2. Botones de Acción
button_frame = Label(root)
button_frame.pack(pady=10)

# Botón Traducir
translate_btn = Button(button_frame, text="Traducir a Morse", command=translate_and_display, bg='#4CAF50', fg='white')
translate_btn.pack(side=LEFT, padx=10)

# Botón Reproducir
play_btn = Button(button_frame, text="▶ Reproducir Sonido", command=play_current_morse, bg='#008CBA', fg='white')
play_btn.pack(side=LEFT, padx=10)


# 3. Visualización del Código Morse
Label(root, text="Código Morse:", font=('Arial', 12, 'bold')).pack(pady=10)
morse_display_label = Label(root, text="---", font=('Consolas', 22), wraplength=580, justify=LEFT)
morse_display_label.pack(fill=X, padx=10)


# Ejecución de la aplicación
if __name__ == "__main__":
    root.mainloop()
    