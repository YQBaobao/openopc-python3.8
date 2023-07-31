#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@Project ：openopc 
@File    ：OpenOPCRPC.py
@Author  ：yqbao
@Date    ：2022/10/10 17:07

SMWinservice
Base class to create winservice in Python
-----------------------------------------
Instructions:
1. Just create a new class that inherits from this base class
2. Define into the new class the variables
   _svc_name_ = "nameOfWinservice"
   _svc_display_name_ = "name of the Winservice that will be displayed in scm"
   _svc_description_ = "description of the Winservice that will be displayed in scm"
3. Override the three main methods:
    def start(self) : if you need to do something at the service initialization.
                      A good idea is to put here the inizialization of the running condition
    def stop(self)  : if you need to do something just before the service is stopped.
                      A good idea is to put here the invalidation of the running condition
    def main(self)  : your actual run loop. Just create a loop based on your running condition
4. Define the entry point of your module calling the method "parse_command_line" of the new class
5. Enjoy
"""
import os
import sys
import win32event
import win32serviceutil
import win32service
import servicemanager
import socket
import logging
import inspect
import winerror
import pickle
from threading import Thread
from multiprocessing.connection import Listener
from multiprocessing.context import AuthenticationError

# 这是除开Pyro4以外，另一种实现远程调用方法的方式，但现在有点问题，就是停止服务时无法杀死可执行文件
__version__ = '1.0.0'

import OpenOPC
from logging.handlers import TimedRotatingFileHandler

opc_class = OpenOPC.OPC_CLASS
opc_gate_host = "0.0.0.0"
opc_gate_port = 27000
opc_obj = object


class RPCHandler(object):
    """RPC注册"""

    def __init__(self):
        self._functions = {}
        self._running = True

    def terminate(self):
        self._running = False

    def register_function(self, function):
        self._functions[function.__name__] = function

    def handle_connection(self, connection):
        try:
            # Receive a message
            while self._running:
                func_name, args, kwargs = pickle.loads(connection.recv())
                # Run the RPC and send a response
                try:
                    r = self._functions[func_name](*args, **kwargs)
                    connection.send(pickle.dumps(r))
                except Exception as e:
                    connection.send(pickle.dumps(e))
        except EOFError:
            pass
        except ConnectionResetError:
            # print("The client has been disconnected! ")
            servicemanager.LogInfoMsg("The client has been disconnected! ")
            pass


class RPC(object):
    """RPC服务"""

    def __init__(self):
        self.sock = None
        self.t = None
        self._running = True

    def terminate(self):
        self._running = False
        self.sock.close()
        self.t.join()

    def rpc_server(self, handlers, address, authkey):
        self.sock = Listener(address, authkey=authkey)
        while True:
            try:
                client = self.sock.accept()
                self.t = Thread(target=handlers.handle_connection, args=(client,))
                self.t.daemon = True
                self.t.start()
            except AuthenticationError:
                pass
            if not self._running:
                break


# Some remote functions
class OPC(object):
    opc_data = None
    message = ''

    @staticmethod
    def welcome_message(name):
        return "Hi welcome " + str(name)

    @staticmethod
    def create_client():
        """Create a new OpenOPC instance"""
        global opc_obj
        opc_obj = OpenOPC.Client(opc_class)

    @staticmethod
    def connect(opc_server):
        opc_obj.connect(opc_server)

    def read(self, group, tags, update):
        self.opc_data = opc_obj.read(tags=tags, group=group, update=update)
        return self.opc_data

    @staticmethod
    def verbose():
        """追踪信息"""

        def trace(msg):
            OPC.message = msg

        opc_obj.set_trace(trace)
        return OPC.message

    @staticmethod
    def remove():
        pass

    @staticmethod
    def close():
        opc_obj.remove(opc_obj.groups())
        opc_obj.close()


class SMWinService(win32serviceutil.ServiceFramework):
    """Base class to create winservice in Python"""
    _svc_name_ = 'PythonService'
    _svc_display_name_ = 'Python Service'
    _svc_description_ = 'Python Service Description'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.run = True

    def _getLogger(self):
        """logging"""
        logger = logging.getLogger(f'[{self._svc_name_}]')
        this_file = inspect.getfile(inspect.currentframe())
        dir_path = os.path.abspath(os.path.dirname(this_file))
        if os.path.isdir('%s\\..\\log' % dir_path):  # 创建log文件夹
            pass
        else:
            os.mkdir('%s\\..\\log' % dir_path)
        dir_path = '%s\\..\\log' % dir_path

        fileHandler = TimedRotatingFileHandler(
            os.path.join(dir_path, "opc.log"), when="midnight", interval=1, backupCount=20)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.setLevel(logging.INFO)
        return logger

    @classmethod
    def parse_command_line(cls):
        """ClassMethod to parse the command line"""
        win32serviceutil.HandleCommandLine(cls)

    def SvcStop(self):
        """Called when the service is asked to stop"""
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Called when the service is asked to start"""
        self.start()
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ''))
        self.main()

    def start(self):
        """
        Override to add logic before the start
        eg. running condition
        """
        pass

    def stop(self):
        """
        Override to add logic before the stop
        eg. invalidating running condition
        """
        pass

    def main(self):
        """Main class to be ovverridden to add logic"""
        pass


class OpcService(SMWinService):
    """注册windows服务"""
    _svc_name_ = "zzzRPCService"
    _svc_display_name_ = "OpenOPCRPCService"
    _svc_description_ = "OpenOPC RPC Gateway Service"

    def __init__(self, args):
        super().__init__(args)
        self.logger = self._getLogger()
        self.handler = RPCHandler()

    def start(self):
        # Register with a handler
        functions = [
            OPC().welcome_message, OPC().create_client,
            OPC().connect, OPC().read, OPC().remove, OPC().close
        ]
        for fun in functions:
            self.handler.register_function(fun)
        self.run = True

    def stop(self):
        self.logger.info("Stopping service...")
        servicemanager.LogInfoMsg('Stopping service...')
        self.handler.terminate()
        RPC().terminate()
        self.run = False

    def main(self):
        """业务主逻辑"""
        self.logger.info("Starting service on port %d" % opc_gate_port)
        servicemanager.LogInfoMsg('Starting service on port %d' % opc_gate_port)
        rpc = RPC()
        # 监听循环
        rpc.rpc_server(self.handler, (opc_gate_host, opc_gate_port), authkey=b'peekaboo', )


def registerService():
    if len(sys.argv) == 1:
        try:
            evt_src_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(OpcService)
            servicemanager.Initialize('zzzRPCService', evt_src_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
    else:
        if sys.argv[1] == '--foreground':
            handler = RPCHandler()
            function = [
                OPC().welcome_message, OPC().create_client,
                OPC().connect, OPC().read, OPC().remove, OPC().close
            ]
            for fu in function:
                handler.register_function(fu)
            rpc_foreground = RPC()
            rpc_foreground.rpc_server(handler, (opc_gate_host, opc_gate_port), authkey=b'peekaboo')
        else:
            win32serviceutil.HandleCommandLine(OpcService)


if __name__ == '__main__':
    registerService()
