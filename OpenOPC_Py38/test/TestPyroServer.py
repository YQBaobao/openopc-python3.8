#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : openopc-Pyro4 
@ File        : TestPyroServer.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : pyro协议时启用
"""
from Pyro4 import configuration, Daemon

from src.OpenOPCService import OPC, opc_gate_host, opc_gate_port

opc = OPC()
configuration.Configuration.SERIALIZERS_ACCEPTED = ["serpent", "marshal"]
daemon = Daemon(host=opc_gate_host, port=opc_gate_port)
ob_uri = daemon.register(opc, 'opc')
print("Object uri =", ob_uri)
daemon.requestLoop()
