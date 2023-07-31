# !/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : openopc-Pyro4
@ File        : StartHttpGateway.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description : 使用http gateway来实现远程访问时启用,使用前需要先启动 OpenOPCNameService 名称服务
"""
import logging
import os

import waitress
from Pyro4.utils.httpgateway import pyro_app
from paste.translogger import TransLogger

from Logssss import init_logging
from OpenOPCNameService import host_ip

init_logging(level=logging.INFO, file=os.path.join(os.getcwd(), 'logs/http-gateway.log'))

http_port = 7767
re = pyro_app.ns_regex = r'remote.opcda.'
app = TransLogger(
    pyro_app,
    logging_level=logging.INFO,
    setup_console_handler=False,
    set_logger_level=logging.WARNING
)
waitress.serve(app, host=host_ip(), port=http_port, url_scheme='http')
