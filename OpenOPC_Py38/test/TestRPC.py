#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : openopc-Pyro4 
@ File        : TestRPC.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
from src.OpenOPCRPC import RPCHandler, OPC, RPC, opc_gate_host, opc_gate_port

handle = RPCHandler()
func = [
    OPC().welcome_message, OPC().create_client,
    OPC().connect, OPC().read, OPC().remove, OPC().close, OPC().verbose
]
for f in func:
    handle.register_function(f)
RPC().rpc_server(handle, (opc_gate_host, opc_gate_port), authkey=b'peekaboo')
