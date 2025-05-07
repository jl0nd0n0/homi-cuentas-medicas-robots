import traceback
import subprocess
#import mysql.connector
import MySQLdb
from dotenv import load_dotenv
import os
import sys
import time

# Get the absolute path of the parent folder
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent folder to sys.path
sys.path.append(parent_folder)
# Cargar variables de entorno desde el archivo .env
# Obtener la ruta absoluta del archivo .env en el directorio superior
env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
# print(env_path)
load_dotenv(env_path)

# Configuración de la conexión a la base de datos usando variables de entorno
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

# Conectar a la base de datos
try:
    # Establish a connection to the database
    connection = MySQLdb.connect(**db_config)
    # Create a cursor object to execute queries
    cursor = connection.cursor()
    
    # Example query
    query = """
        select numero_factura as factura
        from soporte_generar
        where  soporte = 'factura-excel'
          and ifnull(generado, 0) = 0
          and ifnull(robot, 0) = 0;
    """

    # Execute the query
    cursor.execute(query)
    print("paso 001")
    
    # Better: Iterate through results one by one (memory efficient)
    # Count the number of rows
    row_count = len(results)
    if row_count == 0:
        print("No hay resultados ... ")
    for row in cursor.fetchall():
        factura = row[0]
        subprocess.run(["python", "robot-indigo-factura-excel-generar.py", str(factura)])
        #sys.exit()
            
except Exception as e:
    print(f"Error crítico:")
    traceback.print_exc()  # Muestra el error completo    

sys.exit()
print("paso 02")    
    
