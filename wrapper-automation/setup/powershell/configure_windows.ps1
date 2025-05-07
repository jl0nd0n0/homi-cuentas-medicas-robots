# Requiere ejecución como administrador
if (-NOT ([Security.Principal.WindowsPrincipal][Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    echo "Ejecuta este script como administrador"
    exit
}

# Crear script para actualizar IP dinámica
$portUpdateScript = @'
$wsl_ip = (wsl hostname -I).Trim()
netsh interface portproxy delete v4tov4 listenport=2222 | Out-Null
netsh interface portproxy add v4tov4 listenport=2222 listenaddress=0.0.0.0 connectport=22 connectaddress=$wsl_ip | Out-Null
'@ | Out-File "$env:USERPROFILE\update_wsl_ssh.ps1" -Encoding UTF8

# Crear tarea programada para ejecutar al inicio
$action = New-ScheduledTaskAction -Execute "powershell.exe" -Argument "-ExecutionPolicy Bypass -File $env:USERPROFILE\update_wsl_ssh.ps1"
$trigger = New-ScheduledTaskTrigger -AtLogOn
Register-ScheduledTask -Action $action -Trigger $trigger -TaskName "Update WSL SSH Forwarding" -Description "Actualiza el reenvío de puertos para WSL" | Out-Null

# Ejecutar configuración inicial
powershell -ExecutionPolicy Bypass -File "$env:USERPROFILE\update_wsl_ssh.ps1"

Write-Host "Configuración completada!" -ForegroundColor Green
Write-Host "Usa este comando para conectarte desde remoto:"
Write-Host "ssh $env:USERNAME@[IP_WINDOWS] -p 2222" -ForegroundColor Cyan