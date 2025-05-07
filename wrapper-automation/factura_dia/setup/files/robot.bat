@echo off
set logfile=log.txt
set startTime=%time%
echo running at %date% %startTime% >> %logfile%
etl
