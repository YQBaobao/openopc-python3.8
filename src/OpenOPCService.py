###########################################################################
#
# OpenOPC Gateway Service
#
# A Windows service providing remote access to the OpenOPC library.
#
# Copyright (c) 2007-2012 Barry Barnreiter (barry_b@users.sourceforge.net)
# Copyright (c) 2014 Anton D. Kachalov (mouse@yandex.ru)
# Copyright (c) 2017 José A. Maita (jose.a.maita@gmail.com)
# Copyright (c) 2022 Yue BaoBao (yqbaowo@foxmail.com)
#
###########################################################################

import win32serviceutil
import win32service
import win32event
import servicemanager
import winerror
import winreg
import select
import os
import sys
import time
import logging
import inspect

import OpenOPC

__version__ = '1.3.3'

try:
    import Pyro4
    import Pyro4.core
    import win32timezone  # 不要删除，因为打包需要用到
except ImportError:
    print('Pyro4 module required (https://pypi.python.org/pypi/Pyro4)')
    exit()

Pyro4.config.SERVERTYPE = 'thread'
opc_class = OpenOPC.OPC_CLASS
opc_gate_host = "0.0.0.0"
opc_gate_port = 7766


def getvar(env_var):
    """Read system environment variable from registry"""
    try:
        key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                             'SYSTEM\\CurrentControlSet\\Control\\Session Manager\\Environment', 0, winreg.KEY_READ)
        value, value_type = winreg.QueryValueEx(key, env_var)
        return value
    except Exception:
        return None


# Get env vars directly from the Registry since a reboot is normally required
# for the Local System account to inherit these.
if getvar('OPC_CLASS'):  opc_class = getvar('OPC_CLASS')
if getvar('OPC_GATE_HOST'):  opc_gate_host = getvar('OPC_GATE_HOST')
if getvar('OPC_GATE_PORT'):  opc_gate_port = int(getvar('OPC_GATE_PORT'))


@Pyro4.expose  # needed for version 4.55
class OPC(object):
    def __init__(self):
        self._remote_hosts = {}
        self._init_times = {}
        self._tx_times = {}

    @staticmethod
    def welcome_message(name):
        return "Hi welcome " + str(name)

    def get_clients(self):
        """Return list of server instances as a list of (host,init_time,tx_time) tuples"""

        reg1 = Pyro4.core.DaemonObject(self._pyroDaemon).registered()  # needed for version 4.55
        reg2 = [si for si in reg1 if si.find('obj_') == 0]
        reg = ["PYRO:{0}@{1}:{2}".format(obj, opc_gate_host, opc_gate_port) for obj in reg2]
        hosts = self._remote_hosts
        init_times = self._init_times
        tx_times = self._tx_times
        h_list = [(hosts[k] if k in hosts else '', init_times[k], tx_times[k]) for k in reg]
        return h_list

    def create_client(self):
        """Create a new OpenOPC instance in the Pyro server"""
        import re

        opc_obj = OpenOPC.Client(opc_class)
        uri = self._pyroDaemon.register(opc_obj)

        uuid = uri.asString()
        uri_reg_ex = re.compile(r"(?P<protocol>[Pp][Yy][Rr][Oo][a-zA-Z]*):(?P<object>\S+?)(@(?P<location>.+))?$")
        match = uri_reg_ex.match(uuid)
        object_id = match.group("object")

        opc_obj._open_serv = self
        opc_obj._open_self = opc_obj
        opc_obj._open_host = opc_gate_host
        opc_obj._open_port = opc_gate_port
        opc_obj._open_guid = uuid

        self._remote_hosts[uuid] = '%s' % uuid
        self._init_times[uuid] = time.time()
        self._tx_times[uuid] = time.time()
        # return Pyro4.Proxy(uri)
        return object_id

    def release_client(self, obj):
        """Release an OpenOPC instance in the Pyro server"""
        try:
            # Pyro4.Daemon().unregister(obj)
            self._pyroDaemon.unregister(obj)
            del self._remote_hosts[obj.GUID()]
            del self._init_times[obj.GUID()]
            del self._tx_times[obj.GUID()]
            del obj
            return True
        except Exception:
            return False


class OpcService(win32serviceutil.ServiceFramework):
    _svc_name_ = "zzzRMIService"
    _svc_display_name_ = "OpenOPCRMIService"
    _svc_description_ = "OpenOPC Gateway Service"

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
        self.logger.info('Starting service on port %d' % opc_gate_port)
        servicemanager.LogInfoMsg('\n\nStarting service on port %d' % opc_gate_port)

        # 解决错误：Pyro4.errors.SerializeError: serializer 'json' is unknown or not available
        Pyro4.configuration.Configuration.SERIALIZERS_ACCEPTED = ["serpent", "marshal"]

        daemon = Pyro4.Daemon(host=opc_gate_host, port=opc_gate_port)
        daemon.register(OPC(), 'opc')

        socks = daemon.sockets
        while win32event.WaitForSingleObject(self.hWaitStop, 0) != win32event.WAIT_OBJECT_0:
            ins, outs, exs = select.select(socks, [], [], 1)
            if ins:
                daemon.events(ins)
        daemon.shutdown()


def register_service():
    if len(sys.argv) == 1:
        try:
            evt_src_dll = os.path.abspath(servicemanager.__file__)
            servicemanager.PrepareToHostSingle(OpcService)
            servicemanager.Initialize('zzzRMIService', evt_src_dll)
            servicemanager.StartServiceCtrlDispatcher()
        except win32service.error as details:
            if details == winerror.ERROR_FAILED_SERVICE_CONTROLLER_CONNECT:
                win32serviceutil.usage()
                print(' --foreground: Run OpenOPCService in foreground.')
    else:
        if sys.argv[1] == '--foreground':
            daemon_s = Pyro4.Daemon(host=opc_gate_host, port=opc_gate_port)
            daemon_s.register(OPC(), 'opc')

            sock_s = set(daemon_s.sockets)
            while True:
                in_s, out_s, ex_s = select.select(sock_s, [], [], 1)
                if in_s:
                    daemon_s.events(in_s)
        else:
            win32serviceutil.HandleCommandLine(OpcService)


if __name__ == "__main__":
    register_service()
