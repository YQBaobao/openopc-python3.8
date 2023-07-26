# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : openopc-Pyro4 
@ File        : TestHttpGateway.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 使用http gateway来实现远程访问时启用
"""

from Pyro4.utils.httpgateway import main, pyro_app

try:
    re = pyro_app.ns_regex = r'remote.opcda.'
    main(args=['-H', '0.0.0.0', '-p', '7767', '-e', re])
except KeyboardInterrupt:
    print('\n')
