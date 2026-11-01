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


_default_logger = None


def get_logger(log_file=None):
    """
    description: 获取全局日志对象（单例）。全项目统一用它输出日志，不要再用 print
    :param log_file: 首次调用时可指定日志文件路径；不传则默认写到 logs/scripts_logs/run.log
    :return: Logger 实例
    """
    global _default_logger
    if _default_logger is None:
        if log_file is None:
            log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                   "logs", "scripts_logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "run.log")
        _default_logger = Logger(log_file)
    return _default_logger

