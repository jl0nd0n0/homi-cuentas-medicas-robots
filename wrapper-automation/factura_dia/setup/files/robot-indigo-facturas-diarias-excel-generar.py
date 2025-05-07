from dotenv import load_dotenv
import os
import sys
# Get the absolute path of the parent folder
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Add the parent folder to sys.path
sys.path.append(parent_folder)

import pyautogui
from core import robotClick
import time
from pywinauto import Application
from datetime import datetime
import uiautomation as auto
import mysql.connector
import subprocess

path = r"C:\tools\robot\homi\factura_dia"
file = path + rf"\facturas-dia.xlsx"

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

def actualizar_generado(factura):
    """
    Actualiza el campo 'generado' a 1 para la factura especificada.
    
    :param factura: El número de factura a actualizar.
    """
    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Consulta SQL para actualizar el campo 'generado'
        query = """
            UPDATE soporte_generar
            SET generado = 1
            WHERE numero_factura = %s
            and soporte = 'factura-excel'
        """
        # Ejecutar la consulta con el parámetro de la factura
        cursor.execute(query, (factura,))
        connection.commit()

        # Verificar si se realizó la actualización
        if cursor.rowcount > 0:
            print(f"El campo 'generado' ha sido actualizado a 1 para la factura {factura}.")
        else:
            print(f"No se encontró ninguna factura con el número {factura}.")

    except mysql.connector.Error as err:
        print(f"Error al conectar o actualizar en la base de datos: {err}")
    finally:
        # Cerrar la conexión a la base de datos
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")

if len(sys.argv) < 2:
    print("Se requiere como parametro el día para el cual se requiere descargar la facturacion .... ")
    sys.exit()
dia = sys.argv[1]
dia = int(dia)

# Find a window by its title
window = auto.WindowControl(searchDepth=1, AutomationId="FormMdi")
if  not window.Exists():
    print("La ventana no existe !!!")
 
window.SetActive()

# (1)
robotClick(83, 253, 1, "Click Opcion vie RCM")
# (2)
robotClick(317, 162, 1, "Click Facturacion en Salud")
# (3)
robotClick(693, 481, 3, "Click Lista de Facturas")
# (4)
robotClick(237, 180, 1, "Click Input Fecha Inicial")
#dia = datetime.today().day
pyautogui.typewrite(str(dia))
# (5)
robotClick(233, 235, 3, "Click Input Fecha Final")
#pyautogui.typewrite(str(dia + 2))
pyautogui.typewrite("01")
pyautogui.typewrite("05")
pyautogui.typewrite("2025")
# [pyautogui.press('right') for _ in range(5)]
# pyautogui.typewrite("p")
# (6)
robotClick(779, 617, 4, "Click boton generar reporte")
# (7)
robotClick(745, 104, 2, "Click exportar como")
# (8)
robotClick(765, 252, 2, "Click Excel xlsx")
# (9)
robotClick(723, 471, 2, "Click Aceptar")
# (10)
# Crea el directorio si no existe
if not os.path.exists(path):
    os.makedirs(path)
pyautogui.typewrite(file)
auto.SendKeys("{Enter}")
time.sleep(2)
# (11)
robotClick(735, 368, 1, "Click Save as")
# (12)
robotClick(721, 394, 1, "Click No")
# (12)
robotClick(775, 101, 1, "Click No")
subprocess.run(["python", "crear_csv.py"])

# load data to database
# Path to your .bat file
bat_file_path = "robot.bat"
# Run the .bat file
subprocess.run(bat_file_path, shell=True)