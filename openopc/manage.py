#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
import os

import waitress
from paste.translogger import TransLogger
from Pyro4.utils.httpgateway import main, pyro_app

re = pyro_app.ns_regex = r'opc'
# waitress.serve(TransLogger(pyro_app, setup_console_handler=False), host='0.0.0.0', port=8085, url_scheme='http')
main(args=['-H', '0.0.0.0', '-p', '7767', '-e', re])


