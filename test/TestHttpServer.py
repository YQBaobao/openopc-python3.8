# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : openopc-Pyro4
@ File        : TestHttpServer.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 启动名称服务并注册
"""
import time

import Pyro4
from Pyro4 import naming, socketutil
from Pyro4.core import Daemon
from Pyro4.naming import locateNS

from src.OpenOPCNameService import opc_host_name, NSLoopThread, opc_gate_port, OPC

Pyro4.configuration.Configuration.SERIALIZER = "json"
ip_address = socketutil.getIpAddress(opc_host_name, workaround127=True)
ns_uri, name_server, bc_server = naming.startNS(host=ip_address)
bc_server.runInThread()
thread = NSLoopThread(name_server)
thread.start()
thread.running.wait()
time.sleep(0.05)

ns = locateNS(host=ip_address)
daemon_s = Daemon(port=opc_gate_port)
ob_uri = daemon_s.register(OPC(), 'remote.opcda.client')
ns.register('remote.opcda.client', ob_uri)
print("Object URI:", ob_uri)

daemon_s.requestLoop()
