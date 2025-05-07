import os
import sys
import subprocess
import requests
import time
from datetime import datetime

from dotenv import load_dotenv
# Cargar variables de entorno desde el archivo .env
# Obtener la ruta absoluta del archivo .env en el directorio superior
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
# print(env_path)
load_dotenv(env_path)

# URL del endpoint que devuelve {"activo": true} o {"activo": false}
timestamp_ms = int(time.time() * 1000)
URL_ENDPOINT = "https://homi.artemisaips.com/server/php/index.php?x=robot&y=workflow&ts=" + str(timestamp_ms)

# Función para obtener el estado del servidor
def obtener_estado():
    try:
        respuesta = requests.get(URL_ENDPOINT)
        datos = respuesta.json()
        return datos.get("robot", False)
    except Exception as e:
        print(f"[ERROR] No se pudo conectar al endpoint: {e}")
        return False

# Código a ejecutar mientras esté activo
def facturacion_dia(dia, mes, anio):
    try:
        # Change to a specific folder
        os.chdir('factura_dia')
        subprocess.run(["python", "robot-indigo-facturas-diarias-excel-generar.py", dia, mes, anio])
        os.chdir('..')

        # Run the command with two arguments using subprocess.run
        '''
        result = subprocess.run(
            ["python", "factura_dia/robot-indigo-facturas-diarias-excel-generar.py", dia, mes],               # Command + list of arguments
            check=True,                         # Raise an exception if the command fails
            capture_output=True,                # Capture stdout and stderr
            text=True                           # Return output as string instead of bytes
        )
        # Print the output from the command
        print("Command Output:", result.stdout)
        '''

    except subprocess.CalledProcessError as e:
        # Handle any errors that occur during the command execution
        print("An error occurred while executing the command.")
        print("Error Output:", e.stderr)
        
# Bucle principal controlado por el endpoint
try:
    while True:
        robot = obtener_estado()
        print("response: " + str(robot))
        #sys.exit()
        if robot == "factura-dia":
            # pendiente, hacer automaticamente
            # obtener dia, mes, año
            # Obtener la fecha actual
            hoy = datetime.now()

            # Formatear con ceros iniciales para día y mes
            dia = hoy.strftime("%d")   # Día con dos dígitos
            mes = hoy.strftime("%m")   # Mes con dos dígitos
            año = hoy.strftime("%Y")   # Año con cuatro dígitos
            facturacion_dia(dia, mes, año)
            sys.exit()
        else:
            print("[INFO] No me han programado para hacer algo ...")

        # Tiempo de espera antes de volver a consultar (ej: cada 10 segundos)
        time.sleep(1200)

except KeyboardInterrupt:
    print("\n[INFO] Ejecución detenida manualmente.")