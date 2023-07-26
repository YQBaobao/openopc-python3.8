@echo off & setlocal EnableDelayedExpansion

set obj[0]=7767
set port=0
set pid=0
echo Close the HTTP gateway service
for /f "usebackq delims== tokens=1-2" %%a in (`set obj`) do (
    set port=%%b
    for /f "tokens=5" %%m in ('netstat -aon ^| findstr ":%%b"') do (
        set pid=%%m
    )
    if "!pid!"=="0" (
        echo The HTTP gateway service is not started
    ) else (
        echo HTTP Gateway service stopped
        taskkill /f /pid !pid!
    )
    set pid=0
)

pause