# -*- coding: utf-8 -*-

# @author: Jason
# @File: functions.py
# @Time: 4月 20, 2025
# @description:
import time

from adbutils import adb

from common.exec_cmd import ExecuteCommand

ADB_PATH = "/Users/hanguang/.local/bin/adb"

def get_serial_list():
    """
    获取手机列表
    :return:
    """
    serial_list = adb.device_list()
    return serial_list


def get_first_phone_sn():
    """
    获取第一个手机sn号
    :return:
    """
    serial_list = get_serial_list()
    device = serial_list[0]
    sn = device.serial
    return sn


def get_android_platform_verison(sn):
    """
    获取安卓手机平台版本
    :return:
    """
    process = ExecuteCommand(sn)
    cmd = f"{ADB_PATH} -s {sn} shell getprop ro.build.version.release"
    result = process.execute_cmd_output_str(cmd)
    return result


"""
手机操作
"""


def screen_on():
    cmd = f"{ADB_PATH} shell input keyevent 26"
    process = ExecuteCommand()
    process.execute_cmd(cmd)
    time.sleep(1)




if __name__ == '__main__':
    get_android_platform_verison("HMEIUWY9XGNNTKIR")