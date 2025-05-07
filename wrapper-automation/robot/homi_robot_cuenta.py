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

start_time = time.time()

class HomiRobotCuenta:

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
        print("*** HomiRobotCuenta.getFacturas ***")
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
                where  soporte = 'armado-cuenta'
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
                print("voy a generar cuenta: " + str(factura))
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
        print("*** HomiRobotCuenta.getArmado ***")

        def actualizar_estado(factura, boolActualizado = True):
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
                if boolActualizado:
                    query = """
                        call robot_soporte_actualizarGenerado('armado-cuenta', %s, '');
                    """
                    print("Se ha actualizado el estado a generado !")
                else:
                    query = """
                        call robot_soporte_actualizarGenerado('armado-cuenta', %s, 'No se ha encontrado el ingreso, revisar manualmente');
                    """
                    print("Se ha actualizado el estado, no se ha encontrado el ingreso, revisar manual !")
                # Ejecutar la consulta con el parámetro de la factura
                params = (factura,)
                cursor.execute(query, params)
                connection.commit()

                # # Verificar si se realizó la actualización
                # if cursor.rowcount > 0:
                #     print(f"El campo 'generado' ha sido actualizado a 1 para la factura {factura}.")
                # else:
                #     print(f"No se encontró ninguna factura con el número {factura}.")

            except MySQLdb.Error as e:
                print(f"Error: {e}")
                connection.rollback()  # Rollback on error 
            finally:
                # Close connection
                if 'cursor' in locals() and cursor:
                    cursor.close()
                if 'conn' in locals() and connection:
                    connection.close()


        def windowPreviewClose(window):
            # (1)
            #robotClick(495, 422, 2, "click en boton NO abrir este archivo")
            button = window.Control(Name="&No")
            if button.Exists():       
                button.Click()
            
            # (2)
            #robotClick(1351, 12, 1, "click en boton cerrar ventana vista previa (x)")
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.25)

            # (3)
            robotClick(1352, 61, 1, "click en boton cerrar panel (gris)")
            #pyautogui.hotkey('alt', 'f4')
            time.sleep(0.25)

            # (4)
            #robotClick(1352, 61, 1, "click en boton cerrar panel (gris)")
            button = auto.Control(Name="Deshacer")
            if not button.Exists():
                print("El boton deshacer no existe .....")
                sys.exit()
            button.Click()
            print("click en boton deshacer")

            # (5)
            actualizar_estado(factura)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Script executed in {execution_time:.4f} seconds")

        def guardar_soporte(factura):
            # guardar el soporte 
            print("guardar soporte")
            print("Verificar si la ventana esta activa")
            #window = auto.Control(searchDepth=1, Name="Vista previa")
            window = auto.Control(Name="Vista previa")
            if not window.Exists():
                print("No se ha encontrado la ventana !!!!")
            window.SetFocus()

            print("ventana esta lista...")
            if not os.path.exists(file_path):
                # (1)
                button = window.ButtonControl(Name="Exportar Documento...")
                button.Click()
                time.sleep(2)
                #sys.exit()

                #panel = window.PaneControl(Name="Opciones de Exportación PDF")
                #button = panel.ButtonControl(Name="Aceptar")
                #button.Click()
                #time.sleep(1)

                # (2)
                robotClick(707, 555, 2, "click en ACEPTAR exportar PDF")

                # (3)
                pyautogui.typewrite(file_path)
                pyautogui.press('enter')
                time.sleep(2)
                #sys.exit()

                #region subir archivo
                # Definir los archivos
                archivo_local = rf"C:\archivos\proyectos\cartera\armado\cuenta\0000-SOPORTE-ARMADO-CUENTA-{factura}.pdf"
                #SOPORTE_CUENTA_PATH_SERVER = /var/www/html/cdn1.artemisaips.com/public_html/homi/soportes/soportes_factura/files/
                archivo_remoto = f"/var/www/html/cdn1.artemisaips.com/public_html/homi/soportes/soportes_factura/files/{factura}/0000-SOPORTE-ARMADO-CUENTA-{factura}.pdf"
                #sftp_send_file(archivo_local, archivo_remoto)
                #endregion subir archivo

                windowPreviewClose(window)

        def bloqueUIPaciente():
            print("bloqueUIPaciente ..")

            # (4) click en el input de paciente
            robotClick(121, 272, 1)
            auto.SendKeys(identificacion)
            auto.SendKeys("{Enter}") 
            time.sleep(3)

            # (5) click en Combo, validar Auditoria Motivo Consulta
            robotClick(599,330, 1)

            # (6) click, seleccionar validar aspectos clinicos de la atencion
            robotClick(760, 394, 1)
            
            # (7) click boton aceptar
            # OJO NO CAMBIAR A VECES NO TOMA EL FILTRO
            # IMPLEMENTAR CICLO HASTA QUE APAREZCA EL CONTROL SIGUIENTE ..
            robotClick(701, 438, 10, "click en boton aceptar")

            # (8) filtrar por ingreso
            #header = auto.Control(Name="Ingreso")
            #header.Click()
            pyautogui.moveTo(x=117, y=475)
            pyautogui.click(button='right')
            time.sleep(6)

            # (9)
            robotClick(183, 405, 1, "click en filtro")

            # (10) 
            robotClick(475, 230, 1, "click para el filtro de ingreso")
            auto.SendKeys("Ingreso")
            auto.SendKeys("{Enter}")
            time.sleep(1)

            # (11)
            robotClick(615, 230, 0, "click en input, # ingreso ..")
            auto.SendKeys(ingreso)
            auto.SendKeys("{Enter}")

            # (99)
            pyautogui.hotkey('alt', 'a')
            # OJO NO CAMBIAR A VECES NO ALCANZA A ACTUALIZAR LA GRILLA CON LOS INGRESOS ...
            time.sleep(5)
            # determinar si existe el ingreso
            # Locate the table within the application
            table = window.TableControl(AutomationId="INDGridActividades")
            # Ensure the table is found
            if not table.Exists():
                print("Table not found!")
                sys.exit()

            row = table.Control(Name="Fila 1")
            if not row.Exists():
                actualizar_estado(factura, False)
                auto.SendKeys('{Ctrl}{F4}')
            else:
                #"click boton derecho sobre ver folio"
                pyautogui.moveTo(x=119, y=496)
                pyautogui.click(button='right')
                time.sleep(1)
                robotClick(253, 432, 3, "click soporte de cuentas")
                #robotClick(253, 432, 1, "click soporte de cuentas")

                # (99) click para seleccionar todos los de este panel sin el si para que no cargue imagenologia u otros
                robotClick(608, 352, 0.2, "click check historias clinicas")
                robotClick(1314, 350, 0.2, "click check otros soportes")
                robotClick(607, 514, 0.2, "click check reportes de otros profesionales")
                robotClick(1315, 515, 0.2, "click check Otros Documentos")

                robotClick(448, 203, 0, "click imprimir")

                check_interval = 2  # Intervalo de tiempo en segundos entre cada verificación
                print(f"Monitoreando la ventana '{window_title}'...")
                while not isWindowOpen(window_title):
                    print(f"La ventana '{window_title}' no está abierta. Reintentando en {check_interval} segundos...")
                    time.sleep(check_interval)  # Esperar antes de volver a verificar        
                    #robotClick(448, 212, 0, "")

                print(f"¡La ventana '{window_title}' está abierta!")
                guardar_soporte(factura)

        path = r"C:\archivos\proyectos\cartera\armado\cuenta"
        file_path = path + rf"\0000-SOPORTE-ARMADO-CUENTA-{factura}.pdf"

        if os.path.exists(file_path):
            print("El soporte se ha generado anteriormente")
            actualizar_estado(factura)
            end_time = time.time()
            execution_time = end_time - start_time
            print(f"Script executed in {execution_time:.4f} seconds")
            sys.exit()

        # Find a window by its title
        window = auto.WindowControl(searchDepth=1, AutomationId="FormMdi")
        if not window.Exists():
            print("La ventana no existe !!!")

        window.SetActive()
        window_title = "Vista previa"  # Cambia esto al título exacto de la ventana que deseas monitorear
        print("Verificar si la ventana esta abierta ...")
        if isWindowOpen(window_title):
            print("Ventana Vista Previa abierta ...")
            guardar_soporte(factura)
        else:
            window.SetActive()
            #region verificar si existe el panel para busqueda de paciente 
            panel = window.Control(AutomationId="frmHCImpresionHistorias")
            if panel.Exists():
                print("Existe el panel de Consulta de Historias ..  ")
                bloqueUIPaciente()
            else:
            #endregion verificar si existe el panel para busqueda de paciente 
                print("Ventana Vista Previa No Abierta, hay que generar el soporte ...")
                window.SetActive()
                time.sleep(1) 

                path = r"C:\archivos\proyectos\cartera\armado\cuenta"
                file_path = path + rf"\0000-SOPORTE-ARMADO-CUENTA-{factura}.pdf"
                if os.path.exists(file_path):
                    print("ya se ha creado el soporte")
                    actualizar_estado(factura)

                # (0)
                auto.SendKeys('{Ctrl}{F4}')
                # (1)
                robotClick(38, 167, 1, "click en boton View Clinical")
                # (2)
                robotClick(310, 282, 1, "click en boton Cirugia")
                # (3)
                robotClick(624, 326, 7, "click en boton Consulta Historias")

                bloqueUIPaciente()

