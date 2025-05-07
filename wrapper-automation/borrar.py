import time
import uiautomation as auto

time.sleep(3)

# (4)
combo = auto.Control(searchDepth=6, Name="Empresa row0")
combo.Click()
time.sleep(6)

# (5)
button = auto.Control(searchDepth=3, Name="Aceptar")
button.Click()
time.sleep(3)


