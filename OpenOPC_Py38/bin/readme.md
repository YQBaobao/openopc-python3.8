### 运行前检查
1. 运行前先检查当前目录下bat文件是否与下方文说明的文件一致（共6个bat）
2. 检查当前目录下是否存在gbda_aut.dll

### 各个文件的用途：

1. opc.exe 使用说明，请直接使用 -h 参数查看；
2. http-gateway-start.bat:单独启动HTTP网关服务，接收HTTP请求；
3. http-gateway-stop.bat：关闭HTTP网关服务
4. name-service-insatll.bat：安装名称服务和依赖库，安装完成后自动启动，同时启动HTTP网关服务
5. name-service-uninstall.bat：卸载名称服务和依赖库，并关闭HTTP网关服务

注意：下方的RMI服务与上方的服务各选其一即可

6. service-insatll.bat：安装RMI服务和依赖库，安装完成后自动启动
7. service-uninstall.bat：卸载RMI服务和依赖库

### 使用方法：
使用HTTP，直接运行：name-service-insatll.bat
使用RMI，直接运行：service-insatll.bat
