# -*- coding: utf-8 -*-

# @author: Jason
# @File: weichat_utils.py
# @Time: 4月 21, 2025
# @description:微信公共操作函数
import re
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.wait import WebDriverWait

from common.base_test import PageBase
from common.find_ui import find_element_by_android_uiautomator_text, find_element_by_xpath, find_element_by_span_text, \
    find_element_by_a_text, check_element_exist_by_span_text, find_element_by_resource_id


class WeichatUtils(PageBase):

    def __init__(self):
        '''
        description: 初始化
        return:
        '''
        super().__init__()

    def clear_weichat_data(self):
        '''
        description: 清空微信后台数据
        return:
        '''
        self.process.execute_shell_output_str("pm clear com.tencent.mm")

    def wait_for_content(self):
        WebDriverWait(self.driver, 20).until(
            lambda d: any('WEBVIEW' in context for context in d.contexts)
        )

    def switch_content(self, context_exception="WEBVIEW_com.tencent.mm"):
        contexts = self.driver.contexts
        print(f"上下文：{contexts}")
        # 切换到 WebView 上下文
        for context in contexts:
            if 'WEBVIEW' in context and context_exception == context:
                self.driver.switch_to.context(context)
                print(f"已切换到上下文: {context}\n")
                time.sleep(2)
                page_source = self.driver.page_source
                print("页面HTML源码：\n", page_source)
                break

    def click_weichat_search_box(self):
        element = find_element_by_resource_id(self.driver, "com.tencent.mm:id/h5n")
        if element:
            print("点击微信搜索框")
            element.click()
            time.sleep(2)

    def click_home_page_weichat(self):
        element = find_element_by_android_uiautomator_text(self.driver, "微信")
        if element:
            print("点击微信")
            element.click()
            time.sleep(2)

    def click_home_page_file_transporter(self):
        element = find_element_by_android_uiautomator_text(self.driver, "文件传输助手")
        if element:
            print("点击文件传输助手")
            element.click()
            time.sleep(2)

    def click_test_link(self):
        url = "https://test.xunyang.tech/html/webapp/new_test/index.html"
        element = find_element_by_android_uiautomator_text(self.driver, url)
        if element:
            print("点击总链")
            element.click()
            time.sleep(5)

    def click_link_sit(self):
        time.sleep(1)
        element = find_element_by_span_text(self.driver, 'sit')
        if element:
            print("点击总链中sit")
            element.click()
            time.sleep(2)

    def click_link_weixin(self):
        time.sleep(1)
        element = find_element_by_span_text(self.driver, '微信')
        if element:
            print("点击总链中微信")
            element.click()
            time.sleep(2)

    def click_link_title(self, title):
        print('查找标题')
        element = find_element_by_a_text(self.driver, title)
        if element:
            print(f"点击标题:{title}")
            element.click()
            time.sleep(15)

    def check_zhangdan_exit(self):
        result = check_element_exist_by_span_text(self.driver, '账单')
        print(result)

    def launch_weichat(self, timeout=30, restart=False, unlock=True):
        """
        description: 启动微信并等待主界面（底部tab）加载完成
        :param timeout: 等待进入主界面的超时秒数
        :param restart: True 时先 force-stop 再冷启动，保证每次都是干净的首屏
        :param unlock: 是否尝试点亮屏幕并解锁（无密码锁屏场景有效）
        :return: True 表示已就绪
        """
        print("启动微信")
        # 1. 点亮屏幕 + 解锁，避免息屏时启动了却停在锁屏界面
        if unlock:
            self.process.execute_shell_output_str("input keyevent 224")  # KEYCODE_WAKEUP
            time.sleep(0.5)
            self.process.execute_shell_output_str("input keyevent 82")   # KEYCODE_MENU，用于解除无密码锁屏

        # 2. 需要冷启动时先杀进程
        if restart:
            self.force_stop_weichat()
            time.sleep(1)

        current = self.get_current_activity()
        print(f"启动前前台页面：{current}")

        if current.startswith("com.tencent.mm/"):
            print("微信已在前台，直接回到首页")
        else:
            # 优先用 Appium 的 activate_app，失败再回退 adb am start
            try:
                self.driver.activate_app("com.tencent.mm")
                print("已通过 activate_app 启动微信")
            except Exception as e:
                print(f"activate_app 启动失败，回退 am start：{e}")
                self.process.execute_shell_output_str("am start -n com.tencent.mm/.ui.LauncherUI")

        # 3. 等待主界面就绪
        if self.wait_weichat_home(timeout=timeout):
            print("微信启动完成，已进入主界面")
            return True
        raise RuntimeError(f"微信启动超时（{timeout}s），未进入主界面，请检查锁屏、网络或当前页面")

    def force_stop_weichat(self):
        """
        description: 结束后台微信进程
        :return:
        """
        print("结束微信进程")
        self.process.execute_shell_output_str("am force-stop com.tencent.mm")
        time.sleep(1)

    def get_current_activity(self):
        """
        description: 获取当前前台页面，格式如 com.tencent.mm/.ui.LauncherUI
        :return: 前台页面字符串，取不到返回空串
        """
        out = self.process.execute_shell_output_str("dumpsys activity activities")
        # 优先取 topResumedActivity，其次取 mResumedActivity（不同安卓版本字段不同）
        # 输出形如：topResumedActivity=ActivityRecord{d673cf2 u0 com.tencent.mm/.ui.LauncherUI t1787}
        match = re.search(
            r"(?:topResumedActivity|mResumedActivity)\s*=\s*ActivityRecord\{\S+ u\d+ ([\w.]+)/([\w.$]+)",
            out)
        if match:
            return f"{match.group(1)}/{match.group(2)}"
        return ""

    def is_weichat_home(self):
        """
        description: 判断当前是否在微信主界面（底部有"通讯录"tab）
        :return: True/False
        """
        try:
            self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("通讯录")')
            return True
        except Exception:
            return False

    def is_weichat_login_page(self):
        """
        description: 判断当前是否停在微信登录页（清过数据或掉登录态时会出现）
        :return: True/False
        """
        try:
            self.driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("登录")')
            return True
        except Exception:
            return False

    def wait_weichat_home(self, timeout=30):
        """
        description: 等待微信主界面出现；若微信恢复后停在聊天/设置等子页面，自动返回首页
        :param timeout: 超时秒数
        :return: True 表示已到首页，False 表示超时
        """
        start_time = time.time()
        back_times = 0
        while time.time() - start_time < timeout:
            if self.is_weichat_home():
                return True
            if self.is_weichat_login_page():
                raise RuntimeError("微信停留在登录页，请先手动登录后再执行自动化")
            # 启动后仍不在首页，说明恢复到了子页面，返回首页（最多3次）
            if time.time() - start_time > 8 and back_times < 3:
                print(f"当前不在微信首页，执行返回（第{back_times + 1}次）")
                self.driver.back()
                back_times += 1
            time.sleep(1)
        return False

    def get_back(self):
        """
        返回上一页
        :return:
        """
        print("点击返回上一页")
        self.driver.back()

    # ==================== 在微信中打开指定链接 ====================

    def wait_for_element(self, locator, timeout=10):
        """
        description: 显式等待元素出现
        :param locator: (by, value) 元组
        :param timeout: 超时秒数
        :return: element 或 None
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            return wait.until(lambda d: d.find_element(*locator))
        except Exception:
            return None

    def enter_chat_by_search(self, keyword):
        """
        description: 通过顶部搜索进入指定会话（比依赖聊天列表顺序更稳）
        :param keyword: 会话名称，如 "文件传输助手"
        """
        print(f"通过搜索进入会话：{keyword}")
        self.click_weichat_search_box()
        edit = self.wait_for_element((AppiumBy.CLASS_NAME, "android.widget.EditText"), timeout=10)
        if edit is None:
            raise RuntimeError("未找到微信搜索输入框")
        edit.click()
        edit.clear()
        edit.send_keys(keyword)
        time.sleep(1.5)
        target = self.wait_for_element((AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{keyword}")'), timeout=10)
        if target is None:
            raise RuntimeError(f"搜索结果中未找到：{keyword}")
        target.click()
        time.sleep(1.5)

    def send_url_in_current_chat(self, url):
        """
        description: 在当前会话输入框输入链接并发送
        :param url: 要发送的链接
        """
        print(f"发送链接：{url}")
        edit = self.wait_for_element((AppiumBy.CLASS_NAME, "android.widget.EditText"), timeout=10)
        if edit is None:
            raise RuntimeError("未找到聊天输入框")
        edit.click()
        edit.clear()
        edit.send_keys(url)
        time.sleep(1)
        send_btn = self.wait_for_element((AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("发送")'), timeout=5)
        if send_btn is None:
            raise RuntimeError("未找到发送按钮")
        send_btn.click()
        time.sleep(2)

    def wait_and_switch_webview(self, timeout=30, process_hint="tools"):
        """
        description: 等待微信内置浏览器加载并切换到 WEBVIEW 上下文
        :param timeout: 等待超时秒数
        :param process_hint: webview 所在进程关键字，微信 XWeb 一般为 com.tencent.mm:tools
        :return: 切换后的上下文名
        """
        WebDriverWait(self.driver, timeout).until(
            lambda d: any('WEBVIEW' in c for c in d.contexts)
        )
        contexts = self.driver.contexts
        print(f"上下文列表：{contexts}")
        for context in contexts:
            if context.startswith('WEBVIEW') and process_hint in context:
                self.driver.switch_to.context(context)
                print(f"已切换到上下文: {context}")
                time.sleep(2)
                return context
        # 兜底：切第一个 WEBVIEW
        for context in contexts:
            if context.startswith('WEBVIEW'):
                self.driver.switch_to.context(context)
                print(f"兜底切换到上下文: {context}")
                time.sleep(2)
                return context
        raise RuntimeError("未找到可用的 WEBVIEW 上下文")

    def open_url_in_wechat(self, url, wait_webview=30):
        """
        description: 在微信内置浏览器中打开指定链接（完整链路）
                     首页 -> 文件传输助手 -> 已有链接则直接点，否则发送后再点 -> 切WEBVIEW
        :param url: 目标链接
        :param wait_webview: 等待 webview 出现的超时秒数
        """
        self.click_home_page_weichat()
        self.enter_chat_by_search("文件传输助手")

        # 会话里已有相同链接消息就直接点，避免每次重复发送
        msg = self.wait_for_element(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{url}")'), timeout=3)
        if msg is None:
            self.send_url_in_current_chat(url)

        msg = self.wait_for_element(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{url}")'), timeout=5)
        if msg is None:
            raise RuntimeError(f"会话中未找到链接消息：{url}")
        print("点击链接消息")
        msg.click()
        time.sleep(2)
        self.wait_and_switch_webview(timeout=wait_webview)
