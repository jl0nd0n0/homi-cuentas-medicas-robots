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

class HomiRobotImagenologia:

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
        print("*** HomiRobotImagenologia.getFacturas ***")
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
                where  soporte = 'imagenologia'
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
                print("voy a generar imagenologia: " + str(factura))
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
        print("*** HomiRobotImagenologia.getArmado ***")

        def windowPreviewClose():
            #click boton no abrir
            time.sleep(2)
            robotClick(738, 416,1,"boton no abrir")
            robotClick(905, 41,1,"boton no abrir")
            robotClick(1348, 63,1,"boton no abrir")

            actualizar_generado(factura)

        def capturar_pantalla(nombre_archivo, x, y, ancho, alto):
            """
            Captura una región específica de la pantalla y la guarda como una imagen.

            :param nombre_archivo: Nombre del archivo donde se guardará la captura.
            :param x: Coordenada X de la esquina superior izquierda de la región.
            :param y: Coordenada Y de la esquina superior izquierda de la región.
            :param ancho: Ancho de la región a capturar.
            :param alto: Alto de la región a capturar.
            """
            screenshot = pyautogui.screenshot(region=(x, y, ancho, alto))
            screenshot.save(nombre_archivo)
            print(f"Captura guardada como {nombre_archivo}")

        def guardar_soporte(factura, index=0):
            # guardar el soporte 
            print("guardar soporte")

            # Construcción del nombre del archivo con índice
            path = r"C:\archivos\proyectos\cartera\armado\imagenologia"
            suffix = f"-{index}" if index > 0 else ""
            file_path = path + rf"\0001-SOPORTE-ARMADO-IMAGENOLOGIA-{factura}{suffix}.pdf"

            if not os.path.exists(file_path):
                robotClick(43, 37, 5, "click boton guardar")
                pyautogui.typewrite(file_path, interval=0.001)
                pyautogui.press('enter')
                time.sleep(2)
                robotClick(1338, 9, 1, "click boton cerrar")
            else:
                print("ya se ha creado el soporte")
                robotClick(1338, 9, 1, "click boton cerrar")

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
                        call robot_soporte_actualizarGenerado('imagenologia', %s, '')
                    """
                else:
                    query = """
                        call robot_soporte_actualizarGenerado('imagenologia', %s, 'sin soporte')
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
            # click en el input de paciente
            robotClick(124, 269, 1)
            auto.SendKeys(identificacion)
            auto.SendKeys("{Enter}") 
            time.sleep(2)

            #click en validar aspectos clinicos de la atencion
            robotClick(712, 329, 1,"motivo de la consulta")

            robotClick(712, 393, 1,"opcion motivo de la consulta")
            #click boton aceptar
            robotClick(707, 437, 10,"click en boton aceptar")

            #click en Estudios y Documentos
            robotClick(453, 354, 3, "click en Estudios y Documentos")

            #click en Estudios
            robotClick(80, 455, 1, "click en Estudios")

            #quitar el filtro de ingreso, puede generar error si no se hace
            robotClick(55, 659, 1, "click en x para quitar el filtro de ingreso")
            robotClick(1282, 421, 2, "click en aplicar para reiniciar el filtro de ingreso")

            #filtrar por ingreso
            pyautogui.doubleClick(90, 512)
            #robotClick(90, 512, 1, "click en input, # ingreso")
            auto.SendKeys(ingreso)
            auto.SendKeys("{Enter}")
            time.sleep(2)

            contador = 0
            soportes_encontrados = False
            #click en el primer boton de acciones
            while True:
                nombre = f"Acciones row{contador}"
                control = auto.Control(Name=nombre)
                
                if control.Exists():
                    # Tomar títulos de ventanas antes del clic
                    before_titles = get_window_titles()

                    print(f"Haciendo clic en: {nombre}")
                    control.Click()
                    time.sleep(3) 

                    # Tomar títulos de ventanas después del clic
                    after_titles = get_window_titles()

                    # Detectar nuevas ventanas abiertas
                    new_windows = list(set(after_titles) - set(before_titles))

                    if not new_windows:
                        print(f"No se abrió ventana")
                    else:          
                        soportes_encontrados = True  
                        # Guardar el soporte asociado al botón
                        guardar_soporte(factura, contador)

                    contador += 1
                else:
                    print(f"No se encontró más.")
                    break

            #cerrar ventana
            # auto.SendKeys('{Ctrl}{F4}')
            if not soportes_encontrados:
                path_error = r"C:\archivos\proyectos\cartera\armado\imagenologia"
                file_path_error = path_error + rf"\0-SOPORTE-ERROR-IMAGENOLOGIA-{factura}.png"
                if not os.path.exists(file_path_error):
                    capturar_pantalla(
                        nombre_archivo = file_path_error,
                        x=4,
                        y=209,
                        ancho=1356,
                        alto=555
                    )
                actualizar_generado(factura, True)
            else:
                actualizar_generado(factura, False)

            button = auto.Control(Name="Deshacer")
            if not button.Exists():
                print("El boton deshacer no existe .....")
                sys.exit()
            button.Click()
            print("click en boton deshacer")
            

            #filtrar por ingreso
            #header = auto.Control(Name="Ingreso")
            #header.Click()
            # pyautogui.moveTo(x=107, y=477)
            # pyautogui.click(button='right')
            # time.sleep(1)

            # robotClick(453, 354, 1, "click en filtro")
            # robotClick(472, 230, 1, "click para el filtro de ingreso")
            # auto.SendKeys("Ingreso")
            # auto.SendKeys("{Enter}")
            # time.sleep(2)

            # robotClick(626, 230, 1, "click en input, # ingreso ..")
            # auto.SendKeys(ingreso)
            # auto.SendKeys("{Enter}")  

            # # (99)
            # robotClick(726, 522, 1, "click en boton aceptar")
            # # windowFormMdi = auto.Control(Name="FormMdi")
            # # button = windowFormMdi.Control(Name="&Aceptar")
            # # if button.Exists():
            # #     button.Click()

            # #"click boton derecho sobre ver folio"
            # pyautogui.moveTo(x=119, y=496)
            # pyautogui.click(button='right')
            # time.sleep(1)
            # robotClick(253, 432, 1, "click soporte de cuentas")

            # robotClick(422, 251, 2, "click otros documentos")

            # #click filtro de servicio
            # # robotClick(905, 294, 1, "click filtro de servicio")
            # servicio = auto.Control(Name="Servicio")
            # servicio.RightClick()
            # time.sleep(1)

            # filtro = auto.Control(Name="Editor de filtros...")
            # filtro.Click()

            # #editar el filtro
            # robotClick(490, 231, 0.5, "click en tipo de filtro")
            # robotClick(496, 385, 0.5, "seleccionar servicio")
            # robotClick(542, 231, 0.5, "click cambiar tipo de filtro")
            # robotClick(564, 270, 0.5, "click filtro a no es igual")
            # robotClick(606, 231, 0.5, "input del filtro")
            # auto.SendKeys("NO APLICA")
            # auto.SendKeys("{Enter}")
            # robotClick(725, 521, 0.5, "click en Aceptar")
            # time.sleep(1)

        # Find a window by its title
        window = auto.WindowControl(searchDepth=1, AutomationId="FormMdi")
        if  not window.Exists():
            print("La ventana no existe !!!")
        
        window.SetActive()
        time.sleep(1) 

        path = r"C:\archivos\proyectos\cartera\armado\imagenologia"
        file_path = path + rf"\0001-SOPORTE-ARMADO-IMAGENOLOGIA-{factura}.pdf"

        if os.path.exists(file_path):
            print(f"El archivo {file_path} ya existe !!!")
            actualizar_generado(factura)
            sys.exit()

        panel = window.Control(AutomationId="frmHCImpresionHistorias")
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
            # (1)
            robotClick(38, 167, 1, "click en boton View Clinical")
            # (2)
            robotClick(310, 282, 1, "click en boton Cirugia")
            # (3)
            robotClick(624, 326, 7, "click en boton Consulta Historias")

            bloqueUIPaciente()