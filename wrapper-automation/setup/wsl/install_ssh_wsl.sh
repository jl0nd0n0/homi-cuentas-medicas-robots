#!/bin/bash

# Actualizar paquetes
sudo apt update && sudo apt upgrade -y

# Instalar SSH Server
sudo apt install -y openssh-server

# Hacer backup de la configuración original
sudo cp /etc/ssh/sshd_config /etc/ssh/sshd_config.bak

# Configurar SSH (modificar parámetros)
sudo sed -i 's/#PermitRootLogin prohibit-password/PermitRootLogin no/' /etc/ssh/sshd_config
sudo sed -i 's/#PasswordAuthentication yes/PasswordAuthentication yes/' /etc/ssh/sshd_config
sudo sed -i 's/#ListenAddress 0.0.0.0/ListenAddress 0.0.0.0/' /etc/ssh/sshd_config
sudo sed -i 's/#Port 22/Port 22/' /etc/ssh/sshd_config

# Reiniciar servicio SSH
sudo service ssh restart

# Configurar auto-arranque
sudo update-rc.d ssh enable

# Crear regla de firewall en Windows (desde WSL)
echo "Configurando firewall de Windows..."
cmd.exe /c "netsh advfirewall firewall add rule name=\"WSL SSH\" dir=in action=allow protocol=TCP localport=22" 2>/dev/null

# Obtener y mostrar información de conexión
clear
echo "¡Instalación completada!"
echo "Usuario actual: $USER"
echo "Configura tu contraseña con: sudo passwd $USER"
echo "IP de Windows: $(tail -1 /etc/resolv.conf | cut -d' ' -f2)"