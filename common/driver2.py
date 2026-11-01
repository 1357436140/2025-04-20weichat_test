# -*- coding: utf-8 -*-

# @author: Jason
# @File: driver2.py
# @Time: 4月 20, 2025
# @description:
import pytest
from appium import webdriver
from common.functions import get_first_phone_sn, get_android_platform_verison
from common.global_attrs import CHROME_DRIVER_EXECUTABLE


class Driver:

    def __init__(self):
        sn = get_first_phone_sn()
        self.platform_verison = get_android_platform_verison(sn)
        self.device_name = sn
        self.app_package = "com.tencent.mm"
        self.app_activity = "com.tencent.mm.ui.LauncherUI"
        self.chrome_driver = CHROME_DRIVER_EXECUTABLE

    # @pytest.fixture(scope = 'session')
    def get_android_driver(self):
        desired_caps = {
            'automationName': 'UIAutomator2',
            'platformName': 'Android',
            'platformVersion': self.platform_verison,  # 填写android虚拟机/真机的系统版本号
            'deviceName': self.device_name,  # 手机sn号
            'appPackage': self.app_package,  # 填写被测app包名
            'appActivity': self.app_activity,  # 填写被测app的入口
            'noReset': True,  # 是否重置APP
            'unicodeKeyboard': True,  # 是否支持中文输入
            'resetKeyboard': True,  # 是否支持重置键盘
            "chromedriverExecutable": self.chrome_driver

        }
        print(desired_caps)
        driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired_caps)
        return driver

if __name__ == '__main__':
    driver = Driver()
    driver.get_android_driver()