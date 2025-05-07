import socketio
import time

sio = socketio.Client()


@sio.event
def connect():
    print("Conectado al servidor")
    sio.emit('mensaje', {'data': '¡Hola desde Python!'})  # Emitir mensaje dentro del evento 'connect'

@sio.event
def disconnect():
    print("Desconectado del servidor")

# Conectarse al servidor
sio.connect('http://localhost:3001')

@sio.on('confirmacion')
def mensaje_confirmado(data):
    print(f"Servidor respondió: {data}")

#time.sleep(5)
sio.disconnect()  # Mantener la conexión activa
