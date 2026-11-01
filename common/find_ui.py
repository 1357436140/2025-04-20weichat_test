# -*- coding: utf-8 -*-

# @author: Jason
# @File: find_ui.py
# @Time: 4月 20, 2025
# @description: 元素定位相关文件

from selenium.webdriver.common.by import By
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from common.logger import get_logger

"""
元素查找
"""
logger = get_logger()


def find_element_by_resource_id(driver, res_id):
    element = driver.find_element(AppiumBy.ID, res_id)
    return element

def check_element_exist_by_span_text(driver, text):
    """
    通过页面中span对应的文本查找页面元素
    :param driver:
    :param xpath:
    :return:
    """
    logger.info(f"使用span检查页面中元素[{text}]是否存在")
    element = driver.find_element(By.XPATH, f'//span[contains(normalize-space(.),\'{text}\')]')
    if element:
        return True


def find_element_by_android_uiautomator_text(driver, text):
    """
    通过安卓uiautomator的文本方式查找控件
    :param driver:
    :return:
    """
    # element = driver.find_element_by_android_uiautomator(f'new UiSelector().text("{text}")')
    element = driver.find_element(
        AppiumBy.ANDROID_UIAUTOMATOR,
        f'new UiSelector().text("{text}")'
    )
    return element

def find_element_by_span_text(driver, text):
    """
    通过页面中span对应的文本查找页面元素
    :param driver:
    :param xpath:
    :return:
    """
    element = driver.find_element(By.XPATH, f'//span[contains(normalize-space(.),\'{text}\')]')
    return element

def find_element_by_a_text(driver, text):
    """
    通过页面中a对应的文本查找页面元素
    :param driver:
    :param xpath:
    :return:
    """
    element = driver.find_element(By.XPATH, f'//a[contains(normalize-space(),\'{text}\')]')
    return element


def find_element_by_xpath(driver, xpath):
    """
    通过xpath查找页面元素
    :param driver:
    :param xpath:
    :return:
    """
    # element = driver.find_element(By.XPATH, f'{xpath}')
    element = driver.find_element(By.XPATH, '//span[contains(normalize-space(),"回归")]')
    return element

    wait = WebDriverWait(driver, 5)
    ele = wait.until(EC.presence_of_element_located(
        (AppiumBy.XPATH, '//span[text()="回归"]')))


"""
元素点击
"""


