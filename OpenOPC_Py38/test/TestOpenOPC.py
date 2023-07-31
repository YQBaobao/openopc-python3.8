#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : openopc-Pyro4 
@ File        : TestOpenOPC.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 
"""
import time

from src.OpenOPC import Client, OPC_CLASS

OPC_SERVER = 'Kepware.KEPServerEX.V6'
GROUP_NAME = 'group0'
TAG_LIST = [
    u'channel_1.Test_1.K1',
    u'channel_1.Test_7.K7',
    u'channel_2.Test_1.Random1'
]
opc = Client(OPC_CLASS)
opc.connect('Kepware.KEPServerEX.V6')
opc.info()
opc.read(tags=TAG_LIST, group=GROUP_NAME, timeout=5000, sync=True)
try:
    while True:
        # 请求组
        print(opc.properties(tags=TAG_LIST))
        opc_data = opc.read(tags=TAG_LIST, timeout=5000, sync=True)
        send_values = {}
        for item in opc_data:
            name, value, quality, time_ = item
            if quality == 'Good':
                send_values[name] = value
            else:
                print('Error:  {}'.format(item))
            send_values['time'] = time_
        print(send_values)

        time.sleep(2)
finally:
    # 释放资源
    opc.remove(opc.groups())
    opc.close()
