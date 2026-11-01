# -*- coding: utf-8 -*-

# @author: Jason
# @File: watchers.py
# @Time: 4月 20, 2025
# @description: 监听器
from enum import Enum
from typing import Union


class Watchers_chinese(Enum):
    DOWNLOAD = "下载"
    GO_NEXT = "下一步"
    START = "开始体验"
    AGREE = '同意'
    ALLOW = '允许'
    AGREE_CONTINUE = "同意并继续"
    ALLOW_WHILEUSING = "仅在使用中允许"
    ALLOW_WHILEUSING_2 = "仅在使用该应用时允许"
    ALLOW_WHILEUSING_3 = "仅在使用时允许"
    ALLOW_ALWAYS = "总是允许"
    ALLOW_ALWAYS_2 = "始终允许"
    LATER = "以后再说"
    SKIP_AD = "跳过广告"
    SAVE = "保存"
    NEXT_TIME = "下次再说"
    CONFIREM = "确定"
    WAIT = "等待"
    VERIFICATION = "开始验证"
    SKIP = "跳过"
    ENTER_MAINPATE = "进入首页"
    RETRY = "重试"
    ALLOW_PERMISSION_ALL = "允许访问全部"
    KNOW = "知道了"
    SEARCH_DEVICES = "搜索设备"
    CONTINUE = "继续"
    I_KNOW = "我知道了"
    ACCEPT = "接受"
    NOT_OPEN = "暂不开启"
    DECLINE = "拒绝"
    NOT_ALLOW = "不允许"
    GIVE_UP = "舍弃"
    OPEN = "开启"
    REPORT = "报告"
    NOT_UPDATE = "暂不更新"
    UPDATE_NOW = "立即更新"
    INSTALL_LATER = "稍后安装"
    AGREE_CONTINUE_HK = "同意並繼續"
    ALLOW_WHILEUSING_HK = "僅在使用中允許"
    AGREE_CONTINUE_UK = "Agree"
    ALLOW_UK = "Allow"
    ALLOW_WHILEUSING_UK = "Allow only while using the app"
    AGREE_CONTINUE_Arab = "མོས་མཐུན་ཡོད།"
    ALLOW_Arab = "མོས་མཐུན་བྱས་ནས་མུ་མཐུད།"
    ALLOW_WHILEUSING_Arab = "བེད་སྤྱོད་བྱེད་སྐབས་ཆོག་མཆན་སྤྲོད།"
    AGREE_CONTINUE_Uighur = "قوشۇلىمەن"
    ALLOW_Uighur = "قوشۇلۇش ۋە داۋاملاشتۇرۇش"
    ALLOW_WHILEUSING_Uighur = "پەقەت ئىشلەتكەندە رۇخسەت"
    OK = "好的"
    CANCEL = "取消"
    NO_LIMIT = "无限制"
    NO_THANKS = "不用了，谢谢"
    CLOSE_WINDOW_TIP = "按住横杆上滑，可关闭小窗"
    Pairing = '配对'
    TRY_NOW = "立即体验"
    ALLOW_VISIT_ONCE = "允许访问一次"
    ENTER_SPLIT_SCREEN = "进入分屏"
    CLOSE = "关闭"
    ALLOW_THIS_TIME = '允许本次'

class Watchers(Enum):
    DOWNLOAD = "Download"
    GO_NEXT = "Next Step"
    START = "Start Experience"
    AGREE = "Agree"
    ALLOW = "Allow"
    AGREE_CONTINUE = "Agree and Continue"
    ALLOW_WHILEUSING = "Allow While Using"
    ALLOW_WHILEUSING_2 = "Allow Only When Using This App"
    ALLOW_WHILEUSING_3 = "Allow Only When in Use"
    ALLOW_ALWAYS = "Always Allow"
    ALLOW_ALWAYS_2 = "Always Permit"
    LATER = "Ask Me Later"
    SKIP_AD = "Skip Ad"
    SAVE = "Save"
    NEXT_TIME = "Ask Next Time"
    CONFIREM = "Confirm"
    WAIT = "Wait"
    VERIFICATION = "Start Verification"
    SKIP = "Skip"
    ENTER_MAINPATE = "Enter Main Page"
    RETRY = "Retry"
    ALLOW_PERMISSION_ALL = "Grant All Permissions"
    KNOW = "Got It"
    G0_IT= "Got it"
    SEARCH_DEVICES = "Search Devices"
    CONTINUE = "Continue"
    I_KNOW = "I Understand"
    ACCEPT = "Accept"
    ACCEPT1= "ACCEPT"
    NOT_OPEN = "Do Not Open"
    DECLINE = "Decline"
    NOT_ALLOW = "Do Not Allow"
    OPEN = "Open"
    REPORT = "Report"
    NOT_UPDATE = "Do Not Update"
    AGREE_CONTINUE_HK = "Agree and Continue"
    ALLOW_WHILEUSING_HK = "Allow While Using"
    AGREE_CONTINUE_UK = "Agree"
    ALLOW_UK = "Allow"
    ALLOW_WHILEUSING_UK = "Allow only while using the app"
    AGREE_CONTINUE_Arab = "མོས་མཐུན་ཡོད།"
    ALLOW_Arab = "མོས་མཐུན་བྱས་ནས་མུ་མཐུད།"
    ALLOW_WHILEUSING_Arab = "བེད་སྤྱོད་བྱེད་སྐབས་ཆོག་མཆན་སྤྲོད།"
    AGREE_CONTINUE_Uighur = "قوشۇلىمەن"
    ALLOW_Uighur = "قوشۇلۇش ۋە داۋاملاشتۇرۇش"
    ALLOW_WHILEUSING_Uighur = "پەقەت ئىشلەتكەندە رۇخسەت"
    OK = "OK"
    CANCEL = "Cancel"
    NO_LIMIT = "No Limit"
    NO_THANKS = "No Thanks"
    NO_THANKS1 = "No thanks"
    CLOSE_WINDOW_TIP = "Hold the bar and slide up to close the window"
    Pairing = "Pairing"
    TRY_NOW = "Try Now"
    ALLOW_VISIT_ONCE = "Allow Visit Once"
    Not_now  ='Not now'
    MORE = "More"
    WHILE_USING_THE_APP = "while using the app"
    WHILE_USING_THE_APP1='While using the app'
    ALLOW_ALL = "Allow all"
    Turn_on ='Turn on'
    NEXT = "Next"
    OVERALL_HEALTH = "Overall health"
    CONTINUE_AS_LONG = "Continue as Long"
    CLOSE = "Close"
    MORE_DETAILS = "More details"
    DISMISS = "Dismiss"



class LqWatcher:
    def register_watcher(self, device, watcher):
        device.watcher(watcher.name).when(watcher.value).click()
        device.watcher.start()

    def remove_watcher(self, device, watcher_name: Union[str, Enum]):
        if type(watcher_name) is str:
            device.watcher.remove(watcher_name)
        else:
            device.watcher.remove(watcher_name.name)

    def register_watcher_with_callback(self, device, watchers: Union[Watchers, list], func: callable):
        if type(watchers) is Watchers:
            device.watcher(watchers.name).when(watchers.value).call(func)
        else:
            w = device.watcher(watchers[0].name)
            for watcher in watchers:
                w = w.when(watcher.value)
            w.call(func)
        device.watcher.start()


