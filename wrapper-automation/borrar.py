import time
import uiautomation as auto
from datetime import datetime
import os

from robot.homi_robot_factura_dia import HomiRobotFacturaDia

print("paso 01")
time.sleep(3)
print("paso 02")
current_dir = os.getcwd()
current_dir = current_dir + r"\factura_dia"
# Obtener la fecha actual
hoy = datetime.now()
# Formatear con ceros iniciales para día y mes
dia = hoy.strftime("%d")   # Día con dos dígitos
mes = hoy.strftime("%m")   # Mes con dos dígitos
año = hoy.strftime("%Y")   # Año con cuatro dígitos
print("paso 03")
oRobot = HomiRobotFacturaDia(dia, mes, año, current_dir)