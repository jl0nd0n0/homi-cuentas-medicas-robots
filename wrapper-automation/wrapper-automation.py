import subprocess
import requests
import time

from dotenv import load_dotenv
# Cargar variables de entorno desde el archivo .env
# Obtener la ruta absoluta del archivo .env en el directorio superior
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
# print(env_path)
load_dotenv(env_path)

# URL del endpoint que devuelve {"activo": true} o {"activo": false}
URL_ENDPOINT = "https://homi.artemisaips.com/server/php/index.php?x=sanitas&y=" + ROBOT

# Función para obtener el estado del servidor
def obtener_estado():
    try:
        respuesta = requests.get(URL_ENDPOINT)
        datos = respuesta.json()
        return datos.get("activo", False)
    except Exception as e:
        print(f"[ERROR] No se pudo conectar al endpoint: {e}")
        return False

# Código a ejecutar mientras esté activo
def ejecutar_tarea():
    print("[INFO] Ejecutando tarea programada...")
    subprocess.run(["python", "engine-robot-factura-excel-generar.py"])

# Bucle principal controlado por el endpoint
try:
    while True:
        activo = obtener_estado()

        if activo:
            ejecutar_tarea()
        else:
            print("[INFO] Estado inactivo. Esperando nueva actualización...")
        
        # Tiempo de espera antes de volver a consultar (ej: cada 10 segundos)
        time.sleep(10)

except KeyboardInterrupt:
    print("\n[INFO] Ejecución detenida manualmente.")