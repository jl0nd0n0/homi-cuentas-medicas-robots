import os
import sys
# Get the absolute path of the parent folder
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent folder to sys.path
sys.path.append(parent_folder)
import time
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
from sftp import sftp_send_file

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

    def getFacturas(self, boolExcel=False):
        print("*** HomiRobotFactura.getFacturas ***")
        try:
            db_config = {
                "host": os.getenv("DB_HOST"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME")
            }

            # Establish a connection to the database
            connection = MySQLdb.connect(**db_config)
            # Create a cursor object to execute queries
            cursor = connection.cursor()

            if self.año == None:
                strDate = "and fecha = curdate()"
            else:
                strDate = "and fecha = curdate()"
                custom_date = datetime(self.año, self.mes, self.dia)
                formatted = custom_date.strftime("%Y-%m-%d")
                strDate = "and fecha = '" + str(formatted) + "'"

            #print(strDate)
            #sys.exit()
            # Example query
            if (boolExcel):
                query = f"""
                    select numero_factura as factura
                    from soporte_generar
                    where  soporte = 'factura-excel'
                    and ifnull(generado, 0) = 0 
                    {strDate};
                """
            else:
                query = f"""
                    select numero_factura as factura
                    from soporte_generar
                    where  soporte = 'factura'
                    and ifnull(generado, 0) = 0 
                    {strDate};
                """
            #print(query)
            #sys.exit()

            # Execute the query
            cursor.execute(query)

            # Better: Iterate through results one by one (memory efficient)
            results = cursor.fetchall()
            if len(results) == 0:
                return False

            for row in results:
                factura = row[0]
                print("voy a generar factura: " + str(factura))
                self.getFactura(factura, boolExcel)
                # end_time = time.time()
                # duration = end_time - start_time
                # if (duration > 120):
                #     return False

            cursor.close()
            connection.close()

            return True

        except MySQLdb.Error as e:
                print(f"Error: {e}")
                connection.rollback()  # Rollback on error 
        except Exception as e:
            print(f"Error crítico:")
            traceback.print_exc()

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
            #sys.exit()
            auto.SendKeys("{Enter}")
            time.sleep(0.5)

            # (05)
            # guardar como si se despliega
            # button = window.Control(searchDepth=5, AutomationId="CommandButton_6")
            # if button.Exists():
            #     button.Click()
            #     time.sleep(0.25)

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

            if (boolExcel):
                print("factura excel")
                basename = rf"{factura}.xlsx"
                archivo_remoto = f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}"
                sftp_send_file(file_path, archivo_remoto)

                timestamp = int(time.time())

                url = "https://homi.artemisaips.com/server/php/index.php?k=xlsxFactura&x=cargar_v1"
                data = {
                    "p": f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}",
                    "t": timestamp
                }

                response = requests.post(url, data=data)

                if response.ok:
                    print("✅ Respuesta:", response.json())
                else:
                    print("❌ Error:", response.status_code, response.text)
            else:
                print("factura")
                basename = rf"{factura}.pdf"            
                archivo_remoto = f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}"
                sftp_send_file(file_path, archivo_remoto)

            #(07)    
            robotClick(162, 140, 1,"click button deshacer")

            self.updateStatus(factura, boolExcel)
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
            if os.path.exists(file_path):
                print(f"El archivo {file_path} ya existe !!!")
                if (boolExcel):
                    basename = rf"{factura}.xlsx"
                    archivo_remoto = f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}"
                    sftp_send_file(file_path, archivo_remoto)
                else:
                    basename = rf"{factura}.pdf"            
                    archivo_remoto = f"/var/www/html/cdn1.artemisaips.com/public_html/homi/armado/{factura}/{basename}"
                    sftp_send_file(file_path, archivo_remoto)

                self.updateStatus(factura, boolExcel)
                return True

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

        # Configuración de la conexión a la base de datos usando variables de entorno
        db_config = {
            "host": os.getenv("DB_HOST"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "database": os.getenv("DB_NAME")
        }

        #print(file_path)
        #sys.exit()
        fileExists = file_exists(file_path, boolExcel)
        #print(fileExists)
        #sys.exit()
        if fileExists:
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Script executed in {execution_time:.4f} seconds")
            print("")
            #sys.exit()
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
    
    def updateStatus(self, factura, boolExcel=False):                
        """
        Actualiza el campo 'generado' a 1 para la factura especificada.
        
        :param factura: El número de factura a actualizar.
        """
        try:
            print("****** boolExcel: " + str(boolExcel))
            # Establish a connection to the database
            db_config = {
                "host": os.getenv("DB_HOST"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME")
            }
            connection = MySQLdb.connect(**db_config)
            # Create a cursor object to execute queries
            cursor = connection.cursor()        
            # Example query
            # Update query with parameters
            if (boolExcel):
                query = """
                    call robot_soporte_actualizarGenerado('factura-excel', %s, '');
                """
            else:
                query = """
                    call robot_soporte_actualizarGenerado('factura', %s, '');
                """
            
            # Execute the query
            params = (factura,)
            cursor.execute(query, params)
            connection.commit()
            cursor.close()
            connection.close()
            print(f"El campo 'generado' ha sido actualizado a 1 para la factura {factura}.")
        except MySQLdb.Error as e:
            print(f"Error: {e}")
            connection.rollback()  # Rollback on error 
        finally:
            # Close connection
            if 'cursor' in locals() and cursor:
                cursor.close()
            if 'conn' in locals() and connection:
                connection.close()
