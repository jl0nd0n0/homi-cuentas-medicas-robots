@echo off
set param1="%~1"

IF %param1%=="" (
	echo Debe ingresar la fecha
) ELSE (
	echo ----------------------------------------------------------------------
	echo robots HOMI Cargar Facturas Diarias ***************************
	echo ----------------------------------------------------------------------
	echo inicializando tablas ...
	@mysql -vvvvv -u admin -p**p6gaoKmR2TK13mm4w0Yite -h 172.26.0.4 -e "truncate table temporal_facturas_diarias;" homi
	echo Cargando ....

	@mysql -vvvvv -u admin -p**p6gaoKmR2TK13mm4w0Yite -h 172.26.0.4 -e "SET NAMES utf8;SET CHARACTER SET utf8;" homi
	@mysql -vvvvv -u admin -p**p6gaoKmR2TK13mm4w0Yite -h 172.26.0.4 -e "SET GLOBAL local_infile=1;" homi
	@mysql -vvvvv -u admin -p**p6gaoKmR2TK13mm4w0Yite -h 172.26.0.4 --local-infile=1 -e  "LOAD DATA LOCAL INFILE 'facturas-dia.csv' INTO TABLE temporal_facturas_diarias CHARACTER SET utf8mb4 FIELDS TERMINATED BY ';' IGNORE 1 LINES; SHOW WARNINGS;" homi
	@mysql -vvvvv -u admin -p**p6gaoKmR2TK13mm4w0Yite -h 172.26.0.4 -e "call etl_robot_temporal_facturas_diarias('%param1%');" homi
)
