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
from sftp import sftp_send_file

start_time = time.time()

class HomiRobotAdministrativo:

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
        print("*** HomiRobotAdministrativo.getFacturas ***")
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
                select numero_factura as factura,
                    numero_identificacion as identificacion, 
                    ingreso
                from soporte_generar
                where  soporte = 'armado-administrativo'
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
                identificacion = sys.argv[1]
                ingreso = sys.argv[2]
                print("voy a generar administrativo: " + str(factura))
                self.getFactura(factura, identificacion, ingreso)
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

    def getArmado(self, factura, identificacion, ingreso):
        print("*** HomiRobotAdministrativo.getArmado ***")

        def is_window_open(window_title):
            """
            Verifica si una ventana con el título especificado está abierta.
            :param window_title: Título de la ventana a buscar.
            :return: True si la ventana está abierta, False en caso contrario.
            """
            try:
                # Buscar la ventana por su título
                hwnd = win32gui.FindWindow(None, window_title)
                return hwnd != 0  # Retorna True si la ventana existe
            except Exception as e:
                print(f"Error al buscar la ventana: {e}")
                return False

        def actualizar_generado(factura, boolSoporte = False):
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
                if boolSoporte == False:
                    query = """
                        call robot_soporte_actualizarGenerado('armado-administrativo', %s, '')
                    """
                else:
                    query = """
                        call robot_soporte_actualizarGenerado('armado-administrativo', %s, 'sin soporte')
                    """    
                # Ejecutar la consulta con el parámetro de la factura
                print("Se ha actualizado el estado a generado !")
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

        def guardar_soporte(factura, index=0):
            print("guardar soporte")

            # Construcción del nombre del archivo con índice
            path = r"C:\archivos\proyectos\cartera\armado\administrativo"
            suffix = f"-{index}" if index > 0 else ""
            file_path = path + rf"\0001-SOPORTE-ARMADO-ADMINISTRATIVO-{factura}{suffix}.pdf"

            if not os.path.exists(file_path):
                robotClick(43, 37, 5, "click boton guardar")
                pyautogui.typewrite(file_path, interval=0.0001)
                pyautogui.press('enter')
                time.sleep(2)
                robotClick(1338, 9, 1, "click boton cerrar")
            else:
                print("ya se ha creado el soporte")
                robotClick(1338, 9, 1, "click boton cerrar")

        def get_window_titles():
            titles = []

            def enum_handler(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd)
                    if title:
                        titles.append(title)

            win32gui.EnumWindows(enum_handler, None)
            return titles

        def bloqueUIPaciente():
            #input identificacion paciente
            robotClick(144, 260, 1, "click en input Paciente")
            #ingreso identificacion paciente
            auto.SendKeys(identificacion)
            auto.SendKeys("{Enter}") 
            time.sleep(1)

            #input numero ingreso de factura
            robotClick(463, 260, 1, "click en select Ingreso")
            time.sleep(1)
            #mover cursor a filtro
            #robotClick(486, 300, 1, "click en input Ingreso")
            pyautogui.doubleClick(486, 300)
            time.sleep(1)
            #ingreso numero de ingreso de factura
            auto.SendKeys(ingreso)
            robotClick(504, 329, 1, "click en el ingreso de factura")
            time.sleep(2)

            #click boton cargar
            robotClick(732, 263, 1, "click boton cargar")

            #click mover scroll
            robotClick(1354, 694, 1, "click mover scroll")

            # click boton adjuntos
            index = 0
            soportes_encontrados = False

            while True:
                boton_nombre = f"Abrir adjunto row{index}"
                print(f"Buscando botón: {boton_nombre}")

                button = auto.Control(Name=boton_nombre)

                if not button.Exists():
                    print(f"No se encontró el botón con nombre '{boton_nombre}'.")
                    break;
                else:
                    # Tomar títulos de ventanas antes del clic
                    before_titles = get_window_titles()

                    button.Click()
                    time.sleep(5)

                    # Tomar títulos de ventanas después del clic
                    after_titles = get_window_titles()
                    new_windows = list(set(after_titles) - set(before_titles))

                    if not new_windows:
                        print(f"No se abrió ventana al hacer clic en '{boton_nombre}'. Posiblemente el soporte está dañado.")
                    else:
                        soportes_encontrados = True
                        guardar_soporte(factura, index)

                index += 1

            #click cerrar ventana
            button = auto.Control(Name="Deshacer")
            if not button.Exists():
                print("El boton deshacer no existe .....")
                sys.exit()
            button.Click()
            print("click en boton deshacer")
            #click mover scroll
            robotClick(1350, 226, 1, "click mover scroll")

            if not soportes_encontrados:
                actualizar_generado(factura, True)
            else:
                actualizar_generado(factura, False)
            
        # Find a window by its title
        window = auto.WindowControl(searchDepth=1, AutomationId="FormMdi")
        if not window.Exists():
            print("La ventana no existe !!!")

        window.SetActive()

        panel = window.Control(AutomationId="frmADTrazabilidad")
        if panel.Exists():
            print("Existe el panel de Consulta de Historias ..  ")
            bloqueUIPaciente()
        else:
        #endregion verificar si existe el panel para busqueda de paciente 
            print("Ventana Consulta historias No Abierta, hay que generar el soporte ...")
            window.SetActive()
            time.sleep(1)

            # (0)
            auto.SendKeys('{Ctrl}{F4}')
            robotClick(140, 254, 1, "click en VIE RCM")
            robotClick(327, 123, 1, "click en Autorizaciones")
            robotClick(908, 386, 1, "click en Trazabilidad")
            time.sleep(2)
            bloqueUIPaciente()