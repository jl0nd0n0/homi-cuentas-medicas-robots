import pyautogui

# Obtener el tamaño real de la pantalla
screen_width, screen_height = pyautogui.size()
print(f"Resolución de pantalla: {screen_width}x{screen_height}")

print("Mueve el mouse y presiona Ctrl+C para detener...")
try:
    while True:
        x, y = pyautogui.position()
        # Mostrar las coordenadas correctamente formateadas
        print(f"Coordenadas del mouse: ({x}, {y})", end="\r")
except KeyboardInterrupt:
    print("\nDetenido")
