# -*- coding: utf-8 -*-

# @author: Jason
# @File: base_test.py
# @Time: 4月 20, 2025
# @description: 

import os.path
import inspect

import threading
from typing import Union


from adbutils import adb
import time
# from conftest import *
from common.driver import Driver
from common.exec_cmd import ExecuteCommand
from common.functions import screen_on
from common.logger import Logger
from common.watchers import LqWatcher


class BaseTest:

    @classmethod
    def setup_method(cls, method):
        pass
        # cls.lock_settings.clear_lock('1234')
        # cls.lock_settings.clear_lock('123456')
        # screen_on()
        # caller_frame = inspect.currentframe().f_back
        # cls.module_name = inspect.getmodule(caller_frame).__name__
        #
        # cls.test_file_name = ""
        # cls.test_case = method.__name__
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.AGREE)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.ALLOW)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.AGREE_CONTINUE)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.ALLOW_WHILEUSING)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.ALLOW_ALWAYS)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.ALLOW_ALWAYS_2)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.ALLOW_WHILEUSING_3)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.NOT_UPDATE)
        # cls.watchers.register_watcher(cls.d, Watchers_chinese.NEXT_TIME)
        # cls.back_to_homescreen(cls)

    @classmethod
    def teardown(cls):
        # cls.test_end_time = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        # screen_shot = f"{cls.test_case}-{cls.test_end_time}.png"

        # cls.watchers.remove_watcher(cls.d, Watchers.AGREE)
        # cls.watchers.remove_watcher(cls.d, Watchers.ALLOW)
        # cls.watchers.remove_watcher(cls.d, Watchers.AGREE_CONTINUE)
        # cls.watchers.remove_watcher(cls.d, Watchers.ALLOW_WHILEUSING)
        # cls.watchers.remove_watcher(cls.d, Watchers.ALLOW_ALWAYS)
        # cls.watchers.remove_watcher(cls.d, Watchers.ALLOW_ALWAYS_2)
        # cls.back_to_homescreen(cls)
        time.sleep(3)


class PageBase:

    def __init__(self):
        driver_class = Driver()
        self.driver = driver_class.get_android_driver()
        print(self.driver)
        self.sn = driver_class.device_name
        self.process = ExecuteCommand(self.sn)

