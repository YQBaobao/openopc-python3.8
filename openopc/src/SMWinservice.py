#!/usr/bin/env python3
# -*- coding: UTF-8 -*-
"""
@Project ：openopc 
@File    ：SMWinservice.py
@Author  ：yqbao
@Date    ：2022/10/12 13:33

Base class to create winservice in Python
-----------------------------------------
Instructions:
1. Just create a new class that inherits from this base class
2. Define into the new class the variables
   _svc_name_ = "nameOfWinservice"
   _svc_display_name_ = "name of the Winservice that will be displayed in scm"
   _svc_description_ = "description of the Winservice that will be displayed in scm"
3. Override the three main methods:
    def start(self) : if you need to do something at the service initialization.
                      A good idea is to put here the inizialization of the running condition
    def stop(self)  : if you need to do something just before the service is stopped.
                      A good idea is to put here the invalidation of the running condition
    def main(self)  : your actual run loop. Just create a loop based on your running condition
4. Define the entry point of your module calling the method "parse_command_line" of the new class
5. Enjoy
"""
import os
import socket
import logging
import inspect
import win32serviceutil

import servicemanager
import win32event
import win32service
from logging.handlers import TimedRotatingFileHandler


class SMWinservice(win32serviceutil.ServiceFramework):
    """Base class to create winservice in Python"""
    _svc_name_ = 'PythonService'
    _svc_display_name_ = 'Python Service'
    _svc_description_ = 'Python Service Description'

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        socket.setdefaulttimeout(60)
        self.run = True

    def _getLogger(self):
        """logging"""
        logger = logging.getLogger(f'[{self._svc_name_}]')
        this_file = inspect.getfile(inspect.currentframe())
        dir_path = os.path.abspath(os.path.dirname(this_file))
        if os.path.isdir('%s\\..\\log' % dir_path):  # 创建log文件夹
            pass
        else:
            os.mkdir('%s\\..\\log' % dir_path)
        dir_path = '%s\\..\\log' % dir_path

        fileHandler = TimedRotatingFileHandler(
            os.path.join(dir_path, "opc.log"), when="midnight", interval=1, backupCount=20)
        formatter = logging.Formatter('%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
        fileHandler.setFormatter(formatter)
        logger.addHandler(fileHandler)
        logger.setLevel(logging.INFO)
        return logger

    @classmethod
    def parse_command_line(cls):
        """ClassMethod to parse the command line"""
        win32serviceutil.HandleCommandLine(cls)

    def SvcStop(self):
        """Called when the service is asked to stop"""
        self.stop()
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        """Called when the service is asked to start"""
        self.start()
        servicemanager.LogMsg(
            servicemanager.EVENTLOG_INFORMATION_TYPE,
            servicemanager.PYS_SERVICE_STARTED,
            (self._svc_name_, ''))
        self.main()

    def start(self):
        """
        Override to add logic before the start
        eg. running condition
        """
        pass

    def stop(self):
        """
        Override to add logic before the stop
        eg. invalidating running condition
        """
        pass

    def main(self):
        """Main class to be ovverridden to add logic"""
        pass


# entry point of the module: copy and paste into the new module
# ensuring you are calling the "parse_command_line" of the new created class
if __name__ == '__main__':
    SMWinservice.parse_command_line()
