import os
import sys
# Get the absolute path of the parent folder
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent folder to sys.path
sys.path.append(parent_folder)
import time

import mysql.connector
from mysql.connector import errorcode
import MySQLdb

import traceback
import subprocess
import requests
from dotenv import load_dotenv
import pyautogui
from pywinauto import Application
import uiautomation as auto
from robot_socketio import socketio_notificar
from datetime import datetime

from core import isWindowOpen
from core import windowClose
from core import robotClick
# from #sftp import #sftp_send_file
from pathlib import Path

class HomiRobotFactura:

    def __init__(self, dia=None, mes=None, año=None):
        # Get the absolute path of the parent folder
        parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        # Add the parent folder to sys.path
        sys.path.append(parent_folder)
        # Cargar variables de entorno desde el archivo .env
        # Obtener la ruta absoluta del archivo .env en el directorio superior
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        load_dotenv(env_path)

        self.dia = dia
        self.mes = mes
        self.año = año

        self.path = Path(__file__).resolve().parent.parent

    def getFactura(self, factura, boolExcel=False):
        print("*** HomiRobotFactura.getFactura ***")

        def window_preview(boolExcel=False):
             # si el archivo existe borrarlo para ahorrar 4 segundos
            if os.path.exists(file_path):
                os.remove(file_path)

            #windowReportes.SetFocus()
            #click codificacion servicio select
            robotClick(356, 151,1,"codificacion servicio select")
            #click codificacion servicio (manual tarifa)
            robotClick(356, 169,1,"codificacion servicio (manual tarifa)")
            #click codificacion producto select
            robotClick(354, 199,1,"codificacion producto select")
            #click codificacion producto (codigo cum)
            robotClick(358, 258,1,"codificacion producto (codigo cum)")
            #click boton enviar
            robotClick(356, 297,1,"boton enviar")

            # (01)
            #guardado de archivo
            #click boton tipo guarda
            robotClick(874, 44,1,"tipo de guardado")
            time.sleep(0.5)
            #click select opcion pdf guardado

            # (02)
            #print(boolExcel)
            #sys.exit()
            if (boolExcel):
                #auto.moveTo(896, 189)
                robotClick(896, 189,1,"select opcion xlsx guardado")
            else:
                robotClick(869, 67,1,"select opcion pdf guardado")
            #sys.exit()

            # (03)
            #robotClick(722, 470,1,"click button aceptar")
            auto.SendKeys("{Enter}")
            time.sleep(1)
           
            # (04)
            auto.SendKeys(file_path)
            auto.SendKeys("{Enter}")
            time.sleep(0.5)

            # (05)    
            #click boton no abrir    
            #robotClick(738, 416,1,"boton no abrir")
            print("cerrando dialog boton NO")
            #windowDialog.SetFocus()
            auto.SendKeys('%n')    
            time.sleep(1)

            #(06)
            print("cerrando ventana preview")
            #auto.SendKeys("%{F4}")
            windowPreview = window.Control(Name="Visor de Reportes")
            # Find the close button (usually has AutomationId="Close")
            close_button = window.Control(Name="Exit")
            # Click the close button
            if close_button:
                close_button.Click()
            else:
                print("Close button not found.")
            time.sleep(1)

            # actualizar el estado del soporte
            self.updateStatus(factura, boolExcel, 4)

            '''
            if (boolExcel):
                print("factura excel")
                basename = rf"{factura}.xlsx"
                archivo_remoto = f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}"
                #sftp_send_file(file_path, archivo_remoto)

                # timestamp = int(time.time())

                # url = "https://homi.artemisaips.com/server/php/index.php?k=xlsxFactura&x=cargar_v1"
                # data = {
                #     "p": f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}",
                #     "t": timestamp
                # }

                # response = requests.post(url, data=data)

                # if response.ok:
                #     print("✅ Respuesta:", response.json())
                # else:
                #     print("❌ Error:", response.status_code, response.text)
            else:
                print("factura")
                basename = rf"{factura}.pdf"            
                archivo_remoto = f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}"
                ##sftp_send_file(file_path, archivo_remoto)
            '''

            #(07)    
            robotClick(123, 137, 1,"click button deshacer")

            # aqui 01
            #self.updateStatus(factura, boolExcel, 1)
            # Get the directory of the current script

            script_dir = Path(__file__).resolve().parent
            print(f"Script directory: {script_dir}")
            # Path to your .bat file
            bat_file_path = "robot.bat"
            # Run the .bat file
            subprocess.run(bat_file_path, shell=True)

            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Script executed in {execution_time:.4f} seconds")
            print("")

        def window_panel(boolExcel=False):
            window.SetActive()
            print("window_panel")
            #windowPanel.SetFocus()
            #click input texto factura
            pyautogui.doubleClick(476, 291)
            #ingreso numero de factura
            auto.SendKeys(factura)
            auto.SendKeys("{Enter}") 
            time.sleep(4)
            robotClick(483, 614,1,"opcion soporte factura")
            window_title = "Visor de Reportes" 
            check_interval = 2  # Intervalo de tiempo en segundos entre cada verificación
            print(f"Monitoreando la ventana '{window_title}'...")
            while not isWindowOpen(window_title):
                print(f"La ventana '{window_title}' no está abierta. Reintentando en {check_interval} segundos...")
                time.sleep(check_interval)  # Esperar antes de volver a verificar  
            time.sleep(4)
            #print("boolExcel: " + str(boolExcel))
            #sys.exit()
            window_preview(boolExcel)
            end_time = time.time()
            execution_time = end_time - start_time
            #print(f"Script executed in {execution_time:.4f} seconds")

        def file_exists(file_path, boolExcel):
            print("file_exists")
            print(file_path)
            if os.path.exists(file_path):
                print(f"El archivo {file_path} ya existe 001 !!!")
                return True
            else: 
                return False

        start_time = time.time()
        path = r"C:\archivos\proyectos\cartera\armado\factura"
        os.makedirs(path, exist_ok=True)

        #print(boolExcel)
        #sys.exit()
        if (boolExcel):
            print("factura excel")
            file_path = path + rf"\{factura}.xlsx"
        else:
            print("factura")
            file_path = path + rf"\{factura}.pdf"

        #print (file_path)

        # Cargar variables de entorno desde el archivo .env
        # Obtener la ruta absoluta del archivo .env en el directorio superior
        env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
        # print(env_path)
        load_dotenv(env_path)

        fileExists = file_exists(file_path, boolExcel)
        if fileExists:
            end_time = time.time()
            execution_time = end_time - start_time
            self.updateStatus(factura, boolExcel, 3)
            '''
            pathBat = os.path.join(self.path, "factura_dia", "update.bat")
            print(pathBat)
            #subprocess.run(pathBat, shell=True)
            subprocess.run([pathBat, factura])
            sys.exit()
            '''
            print(f"Script executed in {execution_time:.4f} seconds")
            print("")
        else:
            # Find a window by its title
            print("p01")
            window = auto.WindowControl(searchDepth=1, AutomationId="FormMdi")
            if not window.Exists():
                print("La ventana principal de IndiGO no existe !!!")
                sys.exit()
            # si la ventana preview esta cargada ir directamente
            print("p02")
            #windowReportes = window.Control(searchDepth=2, Name="Visor de Reportes")
            if (isWindowOpen("Visor de Reportes")):
                print("*****")
                print("PASO 01")
                print("*****")
                window_preview(boolExcel) 
            else:
                print ("cargando la ventana Trazabilidad de Factura")
                windowTrazabilidad = window.Control(searchDepth=2, Name="Trazabilidad de Factura")
                print ("cargada ....")
                print ("validar si la venta trazabilidad existe .....")
                if (not windowTrazabilidad.Exists()):
                    print("No existe ...")
                    window.SetActive()
                    auto.SendKeys('{Ctrl}{F4}')
                    #click boton Vie RCM
                    robotClick(83, 253, 1, "Opcion vie RCM")
                    #click boton glosas
                    robotClick(342, 199,1,"Opcion glosas")
                    #click boton Trazabilidad de factura
                    robotClick(1145, 602, 8, "trazabilidad de factura")
                    window_panel(boolExcel)
                else:                    
                    print("Existe ...")
                    window_panel(boolExcel)
                    print("*****")
                    print("PASO 03")
                    print("*****")
                    window.SetActive()

            # elif (isWindowOpen("Trazabilidad de Factura")):
            #     print("*****")
            #     print("PASO 02")
            #     print("*****")
            #     window_panel(boolExcel)

            # windowPanel = window.Control(searchDepth=2, Name="Trazabilidad de Factura")
            # print("p03")
            # if windowReportes.Exists():
            #     print("*****")
            #     print("PASO 01")
            #     print("*****")
            #     window_preview(boolExcel)            
            # elif windowPanel.Exists():
            #     print("*****")
            #     print("PASO 02")
            #     print("*****")
            #     window_panel(boolExcel)
            # else:
            #     print("*****")
            #     print("PASO 03")
            #     print("*****")
            #     window.SetActive()
            #     # #click boton cerrar vista previalzacion factura
            #     # robotClick(1260, 64,0.5, "cerrar previsualizacion factura")

            #     # #click icono indigo
            #     # robotClick(25, 34, 1, "Icono Indigo")
            #     #click boton Vie RCM
            #     robotClick(83, 253, 1, "Opcion vie RCM")
            #     #click boton glosas
            #     robotClick(342, 199,1,"Opcion glosas")
            #     #click boton Trazabilidad de factura
            #     robotClick(1145, 602, 8, "trazabilidad de factura")
            #     window_panel(boolExcel)
    
    def updateStatus(self, factura, boolExcel=False, position=0):                
        """
        Actualiza el campo 'generado' a 1 para la factura especificada.
        
        :param factura: El número de factura a actualizar.
        """
        try:
            #print("")   
            print("*** updateStatus *** [" + str(position) + "]")
            print("boolExcel: " + str(boolExcel))
            # Establish a connection to the database

            db_config = {
                "host": os.getenv("DB_HOST"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME")
            }
            #print("... abriendo la conexión ...")
            cnx = mysql.connector.connect(**db_config)
            #print("... configurando el autocommit ...")
            cnx.autocommit = True
            #print("... creando el cursor ...")
            cursor = cnx.cursor()            
            #print("... creando el query ...")
            if (boolExcel):
                query = "call robot_soporte_actualizarGenerado('factura-excel','" + str(factura) + "', '')"
            else:
                query = "call robot_soporte_actualizarGenerado('factura','" + str(factura) + "', '')"
            #print(query)
            #print("... ejecutando el query ...")
            cursor.execute(query)
            #print("... fin ...")
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                print("Something is wrong with your user name or password")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                print("Database does not exist")
            else:
                print(err)
        else:
            # Close connection
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'cnx' in locals() and cnx:
                cnx.close()