import pyautogui
import win32gui
import win32con
import time
import os

# Cargar variables de entorno desde el archivo .env
# Obtener la ruta absoluta del archivo .env en el directorio superior
# env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '.env')
# load_dotenv(env_path)

# Configuración de la conexión a la base de datos usando variables de entorno
db_config = {
    "host": os.getenv("DB_HOST"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "database": os.getenv("DB_NAME")
}

def artemisaRPAClick(button):
    rect = button.rectangle()
    x, y = rect.mid_point()
    pyautogui.click(x, y)

def robotClick(x, y, sleep, message = ""):
    print(message)
    pyautogui.moveTo(x=x, y=y)
    pyautogui.click()
    time.sleep(sleep)

def robotInputWriteText(controlContainer, level, AutomationId, text, sleep):
    inputBox = controlContainer.Control(SearchDepth=level, AutomationId=AutomationId)
    inputBox.SetFocus()
    inputBox.SendKeys(text)
    time.sleep(sleep)

def isWindowOpen(window_title):
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

#def validacionDocumento():
    # Consulta SQL para filtrar registros
    query = """
        SELECT numero_factura as factura
        FROM soporte_generar
        WHERE soporte = 'rips-json'
        AND IFNULL(generado, 0) = 0;
    """

    try:
        # Conectar a la base de datos
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Ejecutar la consulta
        cursor.execute(query)
        results = cursor.fetchall()

        # Iterar sobre los resultados
        for row in results:
            factura = row[0]  # Recuperar el número de factura
            print(f"Procesando factura: {factura}")

            # Llamar al script robot_rips_json_generar.py con la factura como parámetro
            subprocess.run(["python", "robot-indigo-rips-json-generar.py", str(factura)])

    except mysql.connector.Error as err:
        print(f"Error al conectar a la base de datos: {err}")
    except Error as err: 
        print(f"{err}")
    finally:
        # Cerrar la conexión a la base de datos
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a la base de datos cerrada.")
#

def windowClose(window_title):
    # Find the window by its exact title
    hwnd = win32gui.FindWindow(None, "Untitled - Notepad")

    if hwnd != 0:
        # Send WM_CLOSE message to gracefully close the window
        win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
    else:
        print("Window not found.")