#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import inspect
import logging
import os
import socket
import sys
import threading
import time

import select
import servicemanager
import win32event
import win32service
import win32serviceutil
import winerror
import win32timezone  # 打包需要

import Pyro4
from Pyro4 import naming, socketutil
from Pyro4.core import Daemon, expose
from Pyro4.naming import locateNS
from Pyro4.errors import CommunicationError

import OpenOPC

opc_host_name = socket.gethostname()
opc_class = OpenOPC.OPC_CLASS
opc_gate_host = "localhost"
opc_gate_port = 17788


def host_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('8.8.8.8', 80))
        opc_get_host = s.getsockname()[0]
    except Exception:
        print('\n')
    else:
        return opc_get_host
    finally:
        s.close()


@expose
class OPC(object):
    opc_data = None
    message = ''

    def read(self, opc_server, group, tags, timeout, sync):
        self.opc_obj = OpenOPC.Client(opc_class)
        self.opc_obj.connect(opc_server)
        self.opc_data = self.opc_obj.read(tags=tags, group=group, timeout=timeout, sync=sync)
        return self.opc_data

    def info(self, opc_server):
        self.opc_obj = OpenOPC.Client(opc_class)
        self.opc_obj.connect(opc_server)
        opc_info = self.opc_obj.info()
        return opc_info


class NSLoopThread(threading.Thread):
    def __init__(self, nameserver):
        super(NSLoopThread, self).__init__()
        self.setDaemon(True)
        self.nameserver = nameserver
        self.running = threading.Event()
        self.running.clear()

    def run(self):
        self.running.set()
        try:
            self.nameserver.requestLoop()
        except CommunicationError:
            pass  # ignore pyro communication errors


class NameServers(object):
    def __init__(self):
        self.ip_address = socketutil.getIpAddress(opc_host_name, workaround127=True)
        self.ip_address = opc_gate_host
        ns_uri, self.name_server, bc_server = naming.startNS(host=self.ip_address)
        # bc_server.runInThread()
        thread = NSLoopThread(self.name_server)
        thread.start()
        thread.running.wait()
        time.sleep(0.05)

    def start(self):
        # ns = locateNS(hmac_key=os.environ.get('PYRO_HMAC_KEY'))
        ns = locateNS(host=self.ip_address)
        daemon = Daemon(port=opc_gate_port)
        ob_uri = daemon.register(OPC(), 'remote.opcda.client')
        ns.register('remote.opcda.client', ob_uri)
        logging.info("Object URI:{}".format(ob_uri))
        print("Object URI:{}".format(ob_uri))
        return daemon


class HttpOpcService(win32serviceutil.ServiceFramework):
    _svc_name_ = "zzzHTTPService"
    _svc_display_name_ = "OpenOPCHTTPService"
    _svc_description_ = "OpenOPC HTTP Gateway Service"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.logger = self._get_logger()
        self.run = True

    def _get_logger(self):
        logger = logging.getLogger(f'[{self._svc_name_}]')
        this_file = inspect.getfile(inspect.currentframe())
        dir_path = os.path.abspath(os.path.dirname(this_file))
        handler = logging.FileHandler(os.path.join(dir_path, "service.log"))
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
        return logger

    def SvcStop(self):
        self.logger.info("Stopping service....")
        servicemanager.LogInfoMsg('\n\nStopping service')
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)
        self.run = False

    def SvcDoRun(self):
        """
        解決打包后：Pyro4.errors.SerializeError: serializer 'json' is unknown or not available
        方案：将Pyro.util.py中第812、813行：
        812：import importlib
        813：json = importlib.import_module(config.JSON_MODULE)
        注释，并替换为：
        import json
        """
        self.logger.info('Starting service on port %d' % opc_gate_port)
        servicemanager.LogInfoMsg('\n\nStarting service on port %d' % opc_gate_port)

        Pyro4.configuration.Configuration.SERIALIZER = "json"
        name_server = NameServers()
        daemon = name_server.start()
        socks = set(daemon.sockets)
        while win32event.WaitForSingleObject(self.hWaitStop, 0) != win32event.WAIT_OBJECT_0:
            ins, outs, exs = select.select(socks, [], [], 1)
            if ins:
                daemon.events(ins)
        daemon.shutdown()


def register_service():
    if len(sys.argv) == 1:
        try:
            evt_src_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(HttpOpcService)
            servicemanager.Initialize('zzzHTTPService', evt_src_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
                print(' --foreground: Run OpenOPCHTTPService in foreground.')
    else:
        if sys.argv[1] == '--foreground':
            Pyro4.configuration.Configuration.SERIALIZER = "json"
            name_server = NameServers()
            daemon_s = name_server.start()
            sock_s = set(daemon_s.sockets)
            while True:
                try:
                    in_s, out_s, ex_s = select.select(sock_s, [], [], 1)
                    if in_s:
                        daemon_s.events(in_s)
                except KeyboardInterrupt:
                    break
        else:
            win32serviceutil.HandleCommandLine(HttpOpcService)


if __name__ == '__main__':
    register_service()
