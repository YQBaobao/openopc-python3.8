@echo off

echo Start the HTTP gateway service
pushd %~dp0
powershell.exe -command ^ "& {Start-Process -WindowStyle hidden -FilePath .\StartHttpGateway.exe}"
popd
echo Start successfully

pause