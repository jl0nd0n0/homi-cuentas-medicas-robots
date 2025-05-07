import socketio
import time

def socketio_notificar():
    sio = socketio.Client()
    @sio.event
    def connect():
        print("Conectado al servidor")
        sio.emit('mensaje', {'data': 'factura-detalle'})  # Emitir mensaje dentro del evento 'connect'

    @sio.event
    def disconnect():
        print("Desconectado del servidor")

    @sio.on('confirmacion')
    def mensaje_confirmado(data):
        print(f"Servidor respondió: {data}")

    #time.sleep(5)
    # Conectarse al servidor
    sio.connect('ws://localhost:3001')
    sio.disconnect()  # Mantener la conexión activa
    
    

def socketio_notificar_factura(soporte):
    sio = socketio.Client()
    @sio.event
    def connect():
        print("Conectado al servidor")
        # {'data': '¡Hola desde Python!'}
        sio.emit('mensaje', {'data': 'factura'})  # Emitir mensaje dentro del evento 'connect'

    @sio.event
    def disconnect():
        print("Desconectado del servidor")

    @sio.on('confirmacion')
    def mensaje_confirmado(data):
        print(f"Servidor respondió: {data}")

    #time.sleep(5)
    # Conectarse al servidor
    sio.connect('ws://localhost:3001')
    sio.disconnect()  # Mantener la conexión activa