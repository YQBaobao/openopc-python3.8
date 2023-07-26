@echo off

echo Uninstall DA DLL dependent library
Regsvr32 /u gbda_aut.dll

echo Uninstall name service
.\OpenOPCService.exe stop
.\OpenOPCService.exe remove
echo Uninstall complete

pause