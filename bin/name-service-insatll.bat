@echo off

echo Start to register DA DLL dependent library
regsvr32 gbda_aut.dll

echo Start registering name service
.\OpenOPCNameService.exe --startup delayed install
echo The name service is installed and set to start automatically at boot

echo start name service
.\OpenOPCNameService.exe start

echo Start the HTTP gateway service
call http-gateway-start.bat
pause