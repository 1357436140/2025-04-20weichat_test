# -*- coding: utf-8 -*-

# @author: Jason
# @File: logger.py
# @Time: 4月 20, 2025
# @description: 日志打印


import logging
import os
import datetime


class Logger:

    def __init__(self, log_file=None):
        self.file = log_file

        self.format = logging.Formatter('%(asctime)s-%(name)s-%(process)d-%(levelname)s: %(message)s', datefmt="%Y-%m-%d %H:%M:%S")
        self.logger = logging.getLogger('WeichatAutoTest')
        logging.Logger.manager.loggerDict.pop('WeichatAutoTest')
        self.logger.handlers = []
        self.logger.removeHandler(self.logger.handlers)
        self.sth = logging.StreamHandler()
        self.sth.setFormatter(self.format)
        self.logger.addHandler(self.sth)
        self.current_path = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
        self.fh = None
        if log_file is not None:
            self.fh = logging.FileHandler(log_file)
            self.fh.setFormatter(self.format)
            self.logger.addHandler(self.fh)

    def info(self, msg):
        self.logger.setLevel(logging.INFO)
        self.logger.info(msg=msg)

    def debug(self, msg):
        self.logger.setLevel(logging.DEBUG)
        self.logger.debug(msg=msg)

    def warning(self, msg):
        self.logger.setLevel(logging.WARNING)
        self.logger.warning(msg)

    def error(self, msg):
        self.logger.setLevel(logging.ERROR)
        self.logger.error(msg)

    def critical(self, msg):
        self.logger.setLevel(logging.CRITICAL)
        self.logger.critical(msg=msg)

