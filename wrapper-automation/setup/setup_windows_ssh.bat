@echo off
:: Nombre del script: setup_windows_ssh.bat
:: Descripción: Configura el reenvío de puertos y firewall en Windows para SSH en WSL.

setlocal

:: Variables configurables
:: para ver el nombre de la distribucion wsl --list --verbose
set PORT=2222
set WSL_NAME=Ubuntu-24.04  :: Cambia esto por el nombre de tu distribución WSL (ej: Ubuntu, Debian, etc.)

echo [INFO] Deteniendo el servidor SSH de Windows si está activo...
net stop sshd >nul 2>&1

echo [INFO] Obteniendo IP de WSL...
for /f "tokens=*" %%a in ('wsl -d %WSL_NAME% ip addr show eth0 ^| grep "inet\b" ^| awk "{print $2}" ^| cut -d/ -f1') do set WSL_IP=%%a

echo [INFO] IP de WSL: %WSL_IP%

echo [INFO] Configurando reenvío de puertos desde Windows (%PORT%) a WSL (%WSL_IP%:22)...
netsh interface ipv4 delete excludedportrange protocol=tcp %PORT% >nul 2>&1
netsh interface ipv4 add excludedportrange protocol=tcp %PORT% >nul 2>&1
netsh interface ipv4 set interface loopback admin=enabled >nul 2>&1
netsh interface ipv4 set address name="loopback" static 127.0.0.1 255.255.255.255 >nul 2>&1
netsh interface ipv4 add route 0.0.0.0/0 "loopback" %WSL_IP% metric=1 >nul 2>&1
netsh interface ipv4 add route 0.0.0.0/0 "vEthernet (WSL)" %WSL_IP% metric=1 >nul 2>&1
netsh interface ipv4 add route 0.0.0.0/0 "Loopback Pseudo-Interface 1" %WSL_IP% metric=1 >nul 2>&1

echo [INFO] Abriendo el puerto %PORT% en el firewall de Windows...
powershell.exe -Command "New-NetFirewallRule -DisplayName 'SSH WSL' -Direction Inbound -LocalPort %PORT% -Protocol TCP -Action Allow" >nul 2>&1

echo [INFO] Listo! Puedes conectarte desde otra máquina con:
echo      ssh usuario@<IP_DE_WINDOWS> -p %PORT%
echo [INFO] Ejemplo: ssh user@192.168.1.5 -p 2222

endlocal	