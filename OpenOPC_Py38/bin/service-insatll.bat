@echo off

echo Start to register DA DLL dependent library
regsvr32 gbda_aut.dll

echo Start registering name service
.\OpenOPCService.exe --startup delayed install
echo The name service is installed and set to start automatically at boot

echo start name service
.\OpenOPCService.exe start

pause