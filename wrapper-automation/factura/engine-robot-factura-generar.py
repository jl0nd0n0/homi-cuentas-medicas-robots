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

if len(sys.argv) < 2:
    print("Se requiere como parametro el start_time, tiempo de ejecucion del proceso que es la ejecucion de todas las aplicaciones ...")
    sys.exit()
start_time = sys.argv[1]
print("")
print("")
print("start_time: " + str(start_time))
#sys.exit()

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
        where soporte = 'factura'
          and ifnull(generado, 0) = 0;
    """

    # Execute the query
    cursor.execute(query)
    
    # Better: Iterate through results one by one (memory efficient)
    for row in cursor.fetchall():
        factura = row[0]
        print("PASO 2001")
        # Open a log file
        with open("subprocess_output.log", "w") as log_file:
            process = subprocess.Popen(["python", "robot-indigo-factura-generar.py", str(factura)],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True)
            print("PASO 2002")
            # Leer línea por línea
            # Read line by line and log to file (and optionally print)
            for line in process.stdout:
                stripped_line = line.strip()
                if stripped_line:  # Skip empty lines
                    print(stripped_line)         # Print to console
                    log_file.write(stripped_line + "\n")  # Save to log
                    log_file.flush()             # Ensure it's written immediately

            # Wait for the process to finish
            process.wait()
        
            print("")
            print("")
            print("")
            print("**")
            print("PASO 1002")
            end_time = time.time()
            duration = end_time - float(start_time)
            print("engine-robot-factura-generar: " + str(duration))
            if (duration > 120):
                print("exit ....")
                sys.exit()
            
except Exception as e:
    print(f"Error crítico:")
    traceback.print_exc()  # Muestra el error completo    

sys.exit()
print("paso 02")    
    
