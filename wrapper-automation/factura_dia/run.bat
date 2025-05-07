@echo off 
set param1="%~1"

IF %param1%=="" (
	echo Debe ingresar el día a descargar ..
) ELSE (
	python robot-indigo-facturas-diarias-excel-generar.py %1
)

