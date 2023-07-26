@echo off

echo Uninstall DA DLL dependent library
Regsvr32 /u gbda_aut.dll

echo Uninstall name service
.\OpenOPCNameService.exe stop
.\OpenOPCNameService.exe remove
echo Uninstall complete

call http-gateway-stop.bat

pause