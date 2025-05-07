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
import win32gui
from dotenv import load_dotenv
import pyautogui
from pywinauto import Application
import uiautomation as auto
from robot_socketio import socketio_notificar
from datetime import datetime

from core import isWindowOpen
from core import windowClose
from core import robotClick
# from sftp import sftp_send_file

start_time = time.time()

class HomiRobotRips:

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

    def getFacturas(self):
        print("*** HomiRobotRips.getFacturas ***")
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
            query = f"""
                select numero_factura as factura
                from soporte_generar
                where soporte = 'rips-json'
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
                print("voy a generar rips: " + str(factura))
                self.getFactura(factura)
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

    def getArmado(self, factura):
        print("*** HomiRobotRips.getArmado ***")

        def actualizar_generado(factura):
            """
            Actualiza el campo 'generado' a 1 para la factura especificada.
            
            :param factura: El número de factura a actualizar.
            """
            try:
                db_config = {
                    "host": os.getenv("DB_HOST"),
                    "user": os.getenv("DB_USER"),
                    "password": os.getenv("DB_PASSWORD"),
                    "database": os.getenv("DB_NAME")
                }

                # Conectar a la base de datos
                connection = MySQLdb.connect(**db_config)
                cursor = connection.cursor()

                # Consulta SQL para actualizar el campo 'generado'
                query = """
                    call robot_soporte_actualizarGenerado('rips-json', %s, '')
                """
                print("Se ha actualizado el estado a generado !")
                # Ejecutar la consulta con el parámetro de la factura
                params = (factura,)
                cursor.execute(query, params)
                connection.commit()

            except MySQLdb.Error as e:
                print(f"Error: {e}")
                connection.rollback()  # Rollback on error 
            finally:
                # Close connection
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'conn' in locals() and connection:
                    connection.close()

        def bloqueUITrazabilidad():
            # (4) click en boton Unidad Operativa
            robotClick(703, 133, 2)
            robotClick(64, 287, 3)

            # (5) click en boton RIPS Generados
            robotClick(81, 191, 3)

            # (6) click en input de la factura
            #robotClick(176, 247, 1)
            pyautogui.doubleClick(176, 247)

            # (7) digitar la factura
            auto.SendKeys(factura)
            time.sleep(8)

            # (8) click derecho en la factura
            pyautogui.moveTo(x=142, y=275)
            pyautogui.click(button='right')
            time.sleep(1)

            # (9) click en el boton Descargar RIPS (Json, XML, Response)
            # robotClick(207, 377, 2)
            buttonDescarga = auto.Control(Name="Descargar RIPS (Json, XML, Response)")
            if buttonDescarga.Exists():
                buttonDescarga.Click()
            else:
                print("No se ha encontrado el boton de descarga de RIPS (Json, XML, Response)")
                sys.exit()

            # (10) click en la ruta de armado
            time.sleep(1)
            robotClick(609, 355, 2)
            #sys.exit()
            robotClick(619, 316, 2)

            # (11) click en botón Aceptar
            robotClick(705, 499, 2)

            actualizar_generado(factura)

        # Find a window by its title
        window = auto.WindowControl(searchDepth=1, AutomationId="FormMdi")
        if not window.Exists():
            print("La ventana no existe !!!")

        window.SetFocus()
        #time.sleep(2)

        panel = window.Control(AutomationId="FrmElectronicRIPSTraceability")
        if panel.Exists():
            print("Existe el panel de Trazabilidad de validación de RIPS ..  ")
            bloqueUITrazabilidad()
        else:
            print("Ventana Trazabilidad de validación de RIPS No Abierta, hay que generar el soporte ...")
            # (0)
            auto.SendKeys('{Ctrl}{F4}')
            # (1) click en boton View RCM
            robotClick(71, 256, 1)
            # (2) click en boton Facturacion Salud
            robotClick(338, 160, 1)
            # (3) click en boton Trazabilidad de Facturacion de RIPS
            robotClick(1156, 177, 8)

            bloqueUITrazabilidad()