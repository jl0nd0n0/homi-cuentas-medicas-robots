@echo off
for /f %%a in ('powershell.exe -Command "Get-Date -Format yyyy-MM-dd"') do set today=%%a
echo Fecha actual: %today%
set logfile=log.txt
set startTime=%time%
echo running at %date% %startTime% >> %logfile%
etl %today%