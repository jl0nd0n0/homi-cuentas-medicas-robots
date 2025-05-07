import traceback
import subprocess
import MySQLdb
from dotenv import load_dotenv
import os
import sys

# Cargar variables de entorno desde el archivo .env
# Obtener la ruta absoluta del archivo .env en el directorio superior
# print(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# sys.exit()
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
# print(env_path)
load_dotenv(env_path)

# Configuración de la conexión a la base de datos usando variables de entorno
# print(os.getenv("DB_HOST"))
# sys.exit()
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Consulta SQL para filtrar registros
query = """
    SELECT numero_factura as factura, 
        numero_identificacion as identificacion, 
        ingreso
    FROM soporte_generar
    WHERE soporte = 'armado-cuenta'
        and IFNULL(generado, 0) = 0
        and robot = 1;
"""

try:
    # Conectar a la base de datos
    connection = MySQLdb.connect(**db_config)
    cursor = connection.cursor()

    # Ejecutar la consulta
    cursor.execute(query)

    # Iterar sobre los resultados
    for row in cursor.fetchall():
        factura = row[0]  # Recuperar el número de factura
        identificacion = row[1]  # Recuperar el número de identificacion
        ingreso = row[2]  # Recuperar el número de ingreso
        print(f"Procesando factura: {factura}")
        # Ejecutar el script que genera el archivo
        subprocess.run(["python", "robot-indigo-cuenta-generar.py", str(factura), str(identificacion), str(ingreso)])
        #sys.exit()
        # Ruta local esperada del archivo generado
        archivo_local = fr"C:\archivos\proyectos\cartera\armado\cuenta\0000-SOPORTE-ARMADO-CUENTA-{factura}.pdf"

        # Subida al servidor remoto con rclone
        #print(f"Subiendo {archivo_local} al FTP remoto...")
        #subprocess.run([
        #    "rclone", "copy",
        #    archivo_local,
        #    f"morfeo:/public_html/facturas/",
        #    "--progress"
        #])

except Exception as e:
    print(f"Error crítico:")
    traceback.print_exc()