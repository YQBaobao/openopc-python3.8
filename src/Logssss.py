#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@ Project     : openopc-Pyro4
@ File        : Logssss.py
@ Author      : yqbao
@ Version     : V1.0.0
@ Description :
"""

import logging
from logging.handlers import TimedRotatingFileHandler


def init_logging(level=logging.INFO, file='./log.txt'):
    formatter = "[%(asctime)s] {%(name)s:%(lineno)d} %(levelname)s - %(message)s"
    logging.basicConfig(filename=file, level=level, format=formatter)
    logger = logging.getLogger('waitress')
    logger.setLevel(level)
    waitress_handler = TimedRotatingFileHandler(file, when='w1', interval=1, backupCount=4, encoding='utf-8')
    logger.addHandler(waitress_handler)
