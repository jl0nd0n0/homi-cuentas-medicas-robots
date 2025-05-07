import os
import sys
# Get the absolute path of the parent folder
parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
# Add the parent folder to sys.path
sys.path.append(parent_folder)

from dotenv import load_dotenv
import time
import subprocess
from datetime import datetime
import MySQLdb
from robot.homi_robot_factura import HomiRobotFactura
from robot.homi_robot_factura_dia import HomiRobotFacturaDia
from robot.homi_robot_cuenta import HomiRobotCuenta
from robot.homi_robot_imagenologia import HomiRobotImagenologia
from robot.homi_robot_administrativos import HomiRobotAdministrativo
from robot.homi_robot_rips import HomiRobotRips

from pywinauto import Application
from core import isWindowOpen
from pywinauto import Desktop
import pyautogui

from core import artemisaRPAClick
from core import robotClick
from core import robotInputWriteText

import uiautomation as auto

class HomiRobot:

    # def __init__(self):
    #     print("HomiRobot initialized")

    '''
    def run(self):
        print("*** HomiRobot.run ***")
        start_time = 0
        oRobot = HomiRobotFactura()
        oRobotCuenta = HomiRobotCuenta()
        oRobotImagenologia = HomiRobotImagenologia()
        oRobotAdministrativo = HomiRobotAdministrativo()
        while True:
            self.procesarFacturaExcel = oRobot.getFacturas(True)
            print("factura excel procesar: " + str(self.procesarFacturaExcel))
            if (not self.procesarFacturaExcel):
                self.procesarFactura = oRobot.getFacturas(False)
                print("factura procesar: " + str(self.procesarFactura))

                if (not self.procesarFactura):
                    self.procesarCuenta = oRobotCuenta.getFacturas()
                    print("cuenta procesar: " + str(self.procesarCuenta)) 

                    if (not self.procesarCuenta):
                        self.procesarImagenologia = oRobotImagenologia.getFacturas()
                        print("imagenologia procesar: " + str(self.procesarImagenologia))

                        if (not self.procesarImagenologia):
                            self.procesarAdministrativo = oRobotAdministrativo.getFacturas()
                            print("administrativo procesar: " + str(self.procesarAdministrativo))

            if (not self.procesarFacturaExcel and not self.procesarFactura):
                self.factura_dia()
    '''

    def factura_dia(self):
        print("*** HomiRobot.factura_dia ***")

        def procesar():
            current_dir = os.getcwd()
            current_dir = current_dir + r"\factura_dia"
            # Obtener la fecha actual
            hoy = datetime.now()
            # Formatear con ceros iniciales para día y mes
            dia = hoy.strftime("%d")   # Día con dos dígitos
            mes = hoy.strftime("%m")   # Mes con dos dígitos
            año = hoy.strftime("%Y")   # Año con cuatro dígitos

            self.startTime = time.time()
            oRobot = HomiRobotFacturaDia(dia, mes, año, current_dir)
            self.endTime = time.time()
            self.duration =  self.endTime - self.startTime

        # si no se ha asignado el endTime, es suficiente para correr la primera vez
        if not hasattr(self, 'endTime'):
            procesar()

        # si han pasado 20 minutos
        if (self.duration >= 120):
            procesar()
        else:
            #print(self.startTime)
            self.endTime = time.time()
            #print(self.endTime)
            self.duration = self.endTime - self.startTime
            print("duracion: " + str(self.duration))
            print("Esperando 20 minutos desde la ultima ejecucion ...")

    def login(self):
        print("*** login ***")

        def windowElementExists(automation_id):
            # Reemplaza con el ejecutable de la app que deseas controlar
            app = Application(backend="uia").connect(title="Login Vie Cloud Native Client")

            # Obtener la ventana principal
            window = app.window(title="Login Vie Cloud Native Client")
            #window.print_control_identifiers()

            # Buscar el elemento por su AutomationId
            element = window.child_window(auto_id=automation_id)
            return element

        def robotWindowLogin():
            print("*** robotWindowLogin ***")
            windowLogin = auto.Control(searchDepth=1, Name="Login Vie Cloud Native Client")
            if not windowLogin.Exists():
                print("No existe la ventana de login, abriendo IndiGO ...")
                appref_path = r"C:\tools\VieCloudPlatform.appref-ms"
                os.startfile(appref_path)

            while not windowLogin.Exists():
                print("ventana login no existe ...")
                windowLogin = auto.Control(searchDepth=1, Name="Login Vie Cloud Native Client")
            
            print("Buscando boton de login ...")
            button = windowLogin.Control(SearchDepth=9, AutomationId="IndigoExchange")
            while not button.Exists():
                print("Boton login windows no existe")
                button = windowLogin.Control(SearchDepth=9, AutomationId="IndigoExchange")
            print("boton Login existe")
            windowLogin.SetFocus()
            time.sleep(3)
            # Get the clickable point (if supported)
            #clickable_point = button.GetClickablePoint()
            # Alternatively, get the control's bounding rectangle and calculate the center
            rect = button.BoundingRectangle
            center_x = (rect.left + rect.right) // 2
            center_y = (rect.top + rect.bottom) // 2
            # Fallback to center of the control
            robotClick(center_x, center_y, 3,"click boton login")
            #robotClick(center_x, center_y, 3,"click boton login")
            #sys.exit()

            # (1)
            robotInputWriteText(auto, 15, "i0116", "jlondonol@homifundacion.org.co", 1)
            auto.SendKeys("{Enter}")
            time.sleep(3)
            # Send the Tab key 3 times
            #button = auto.Control(searchDepth=15, Name="Siguiente")
            #button.Click()
            #sys.exit()

            '''
            inputBox = windowLogin.Control(SearchDepth=13, AutomationId="i0116")
            inputBox.SetFocus()
            inputBox.SendKeys('jlondonol@homifundacion.org.co')
            time.sleep(1)
            auto.SendKeys("{Enter}")
            time.sleep(3)
            '''

            # (2)
            robotInputWriteText(auto, 15, "i0118", "Homi++2025", 1)
            auto.SendKeys("{Enter}")
            time.sleep(3)

            '''
            # (3)
            grid = auto.Control(searchDepth=5, Name="Empresa filter row")
            grid.Click()
            time.sleep(2)

            # (4)
            combo = auto.Control(searchDepth=5, Name="Empresa filter row")
            combo.Click()
            time.sleep(5)
            '''

            # (3)
            combo = auto.Control(searchDepth=6, Name="Empresa row0")
            combo.Click()
            time.sleep(6)
            

            # (4)
            button = auto.Control(searchDepth=3, Name="Aceptar")
            button.Click()
            time.sleep(3)

        robotWindowLogin()

    def soporteGetSiguiente(self):
        print("**** soporteGetSiguiente ****")

        window = auto.WindowControl(searchDepth=1, AutomationId="FormMdi")
        if not window.Exists():
            self.login()

        while True:
            # Get the absolute path of the parent folder
            parent_folder = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            # Add the parent folder to sys.path
            sys.path.append(parent_folder)
            # Cargar variables de entorno desde el archivo .env
            # Obtener la ruta absoluta del archivo .env en el directorio superior
            env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
            # print(env_path)
            load_dotenv(env_path)

            db_config = {
                "host": os.getenv("DB_HOST"),
                "user": os.getenv("DB_USER"),
                "password": os.getenv("DB_PASSWORD"),
                "database": os.getenv("DB_NAME")
            }

            #print(db_config);
            #sys.exit()

            # Establish a connection to the database
            connection = MySQLdb.connect(**db_config)
            # Create a cursor object to execute queries
            cursor = connection.cursor()
            query = """
                call robot_soporte_getNext();
            """
            
            cursor.execute(query)

            # Cargar datos en variables
            resultado = cursor.fetchone()
            #print(resultado)
            #sys.exit()

            if resultado:
                print("*** a seleccionar el robot ***")
                soporte, factura, identificacion, ingreso, err = resultado  # Asignar valores a variables
                print(f"soporte: {soporte}, factura: {factura}")
                if (soporte == 'factura-excel'):
                    oRobotFactura = HomiRobotFactura()
                    oRobotFactura.getFactura(factura, True)
                elif (soporte == 'factura'):
                    oRobotFactura = HomiRobotFactura()
                    oRobotFactura.getFactura(factura, False)
                elif (soporte == 'armado-cuenta'):
                    oRobotCuenta = HomiRobotCuenta()
                    oRobotCuenta.getArmado(factura, identificacion, ingreso)
                elif (soporte == 'imagenologia'):
                    oRobotImagenologia = HomiRobotImagenologia()
                    oRobotImagenologia.getArmado(factura, identificacion, ingreso)
                elif (soporte == 'armado-administrativo'):
                    oRobotAdministrativo = HomiRobotAdministrativo()
                    oRobotAdministrativo.getArmado(factura, identificacion, ingreso)
                elif (soporte == 'rips-json'):
                    oRobotRips = HomiRobotRips()
                    oRobotRips.getArmado(factura)
                else:
                    oRobotFacturaDia = HomiRobot()
                    oRobotFacturaDia.factura_dia()
        
            
            cursor.close()
            connection.close()