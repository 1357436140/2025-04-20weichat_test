# -*- coding: utf-8 -*-
# @author: Jason
# @File: driver2.py
# @Time: 4月 20, 2025
# @description: Mac Appium2 微信鸿蒙驱动
import time
from appium import webdriver
from appium.options.android import UiAutomator2Options
from common.functions import get_first_phone_sn, get_android_platform_verison
from common.global_attrs import CHROME_DRIVER_EXECUTABLE
from appium.webdriver.common.appiumby import AppiumBy

class Driver:
    def __init__(self):
        self.sn = get_first_phone_sn()
        self.platform_verison = get_android_platform_verison(self.sn)
        self.device_name = self.sn
        self.app_package = "com.tencent.mm"
        self.app_activity = ".ui.LauncherUI"
        self.chrome_driver = CHROME_DRIVER_EXECUTABLE

    def get_android_driver(self):
        desired_caps = {
            'platformName': 'Android',
            'platformVersion': self.platform_verison,
            'deviceName': self.device_name,
            'appPackage': self.app_package,
            'appActivity': self.app_activity,
            "appium:appWaitActivity": ".ui.LauncherUI",
            'automationName': 'UiAutomator2',
            'noReset': True,
            'unicodeKeyboard': True,
            'resetKeyboard': True,
            'chromedriverExecutable': self.chrome_driver,
            'adbExecTimeout': 30000,
            # 微信XWeb进程，新版微信在 com.tencent.mm:tools
            'chromeOptions': {
                "androidProcess": "com.tencent.mm:tools"
            }
        }
        print("cap配置：", desired_caps)
        # Appium2 必须用 options 加载 capabilities
        options = UiAutomator2Options().load_capabilities(desired_caps)
        # 注意：地址不要写 /wd/hub！Appium2 默认不需要这个后缀
        driver = webdriver.Remote('http://127.0.0.1:4723', options=options)
        return driver


if __name__ == '__main__':
    try:
        dr = Driver()
        driver = dr.get_android_driver()
        print("✅ driver 创建成功")
        element = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("微信")')
        print(element)


        # time.sleep(3)
        # contexts = driver.contexts
        # print("所有上下文列表：", contexts)
        # # 切换 WEBVIEW
        # for ctx in contexts:
        #     if "WEBVIEW" in ctx:
        #         driver.switch_to.context(ctx)
        #         print(f"✅ 已切换到 {ctx}")
        #         break
        # time.sleep(5)
        driver.quit()
    except Exception as e:
        print(f"❌ 启动失败: {e}")
