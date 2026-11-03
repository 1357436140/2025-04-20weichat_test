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
from common.logger import get_logger
from common.assert_utils import AssertUtils
from common.find_ui import find_element_by_android_uiautomator_text, find_element_by_xpath, find_element_by_span_text, \
    find_element_by_a_text, check_element_exist_by_span_text, find_element_by_resource_id


logger = get_logger()


class WeichatUtils(PageBase):

    def __init__(self):
        '''
        description: 初始化
        return:
        '''
        super().__init__()
        # 断言工具：公共方法内部调用，校验不通过直接抛 AssertionError
        self.assert_util = AssertUtils()

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
        logger.info(f"上下文：{contexts}")
        # 切换到 WebView 上下文
        for context in contexts:
            if 'WEBVIEW' in context and context_exception == context:
                self.driver.switch_to.context(context)
                logger.info(f"已切换到上下文: {context}\n")
                time.sleep(2)
                page_source = self.driver.page_source
                logger.info(f"页面HTML源码：\n{page_source}")
                break

    def click_weichat_search_box(self):
        element = find_element_by_resource_id(self.driver, "com.tencent.mm:id/h5n")
        if element:
            logger.info("点击微信搜索框")
            element.click()
            time.sleep(2)

    def click_home_page_weichat(self):
        element = find_element_by_android_uiautomator_text(self.driver, "微信")
        if element:
            logger.info("点击微信")
            element.click()
            time.sleep(2)

    def click_home_page_file_transporter(self):
        element = find_element_by_android_uiautomator_text(self.driver, "文件传输助手")
        if element:
            logger.info("点击文件传输助手")
            element.click()
            time.sleep(2)

    def click_test_link(self):
        url = "https://test.xunyang.tech/html/webapp/new_test/index.html"
        element = find_element_by_android_uiautomator_text(self.driver, url)
        if element:
            logger.info("点击总链")
            element.click()
            time.sleep(5)

    def click_link_sit(self):
        """
        description: 点击总链首页的「sit」环境（内部先断言入口存在）
        :return: True
        """
        time.sleep(1)
        element = self.assert_util.assert_span_text_present(
            self.driver, 'sit', msg="总链首页未出现「sit」环境入口，请确认页面已加载")
        logger.info("点击总链中sit")
        element.click()
        time.sleep(2)
        return True

    def click_link_weixin(self):
        """
        description: 点击 sit 环境下的「微信」渠道（内部先断言入口存在）
        :return: True
        """
        time.sleep(1)
        element = self.assert_util.assert_span_text_present(
            self.driver, '微信', msg="sit 环境页未出现「微信」渠道入口")
        logger.info("点击总链中微信")
        element.click()
        time.sleep(2)
        return True

    def click_link_title(self, title):
        """
        description: 点击指定标题的 H5 链接（内部先断言链接存在）
        :param title: 链接标题，如 "1、账单查询"
        :return: True
        """
        logger.info(f"查找标题：{title}")
        element = self.assert_util.assert_a_text_present(
            self.driver, title, timeout=15, msg=f"页面未出现链接「{title}」")
        logger.info(f"点击标题:{title}")
        element.click()
        time.sleep(15)
        return True

    def check_zhangdan_exit(self):
        """
        description: 断言账单查询页已渲染出「账单」元素（失效即抛断言异常）
        :return: True
        """
        self.assert_util.assert_span_text_present(
            self.driver, '账单', msg="账单查询页面未出现「账单」元素")
        return True

    def launch_weichat(self, timeout=30, restart=False, unlock=True):
        """
        description: 启动微信并等待主界面（底部tab）加载完成
        :param timeout: 等待进入主界面的超时秒数
        :param restart: True 时先 force-stop 再冷启动，保证每次都是干净的首屏
        :param unlock: 是否尝试点亮屏幕并解锁（无密码锁屏场景有效）
        :return: True 表示已就绪
        """
        logger.info("启动微信")
        # 0. 微信 8.0.7x+ 屏蔽第三方无障碍，必须先开读屏服务才能定位元素
        self.enable_talkback()
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
        logger.info(f"启动前前台页面：{current}")

        if current.startswith("com.tencent.mm/"):
            logger.info("微信已在前台，直接回到首页")
        else:
            # 优先用 Appium 的 activate_app，失败再回退 adb am start
            try:
                self.driver.activate_app("com.tencent.mm")
                logger.info("已通过 activate_app 启动微信")
            except Exception as e:
                logger.info(f"activate_app 启动失败，回退 am start：{e}")
                self.process.execute_shell_output_str("am start -n com.tencent.mm/.ui.LauncherUI")

        # 3. 等待主界面就绪
        if self.wait_weichat_home(timeout=timeout):
            logger.info("微信启动完成，已进入主界面")
            return True
        raise RuntimeError(f"微信启动超时（{timeout}s），未进入主界面，请检查锁屏、网络或当前页面")

    def force_stop_weichat(self):
        """
        description: 结束后台微信进程
        :return:
        """
        logger.info("结束微信进程")
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
        description: 等待微信主界面出现；若微信恢复到聊天/设置等子页面自动返回首页，
                     若被按退到桌面则重新拉起微信
        :param timeout: 超时秒数
        :return: True 表示已到首页，False 表示超时
        """
        start_time = time.time()
        back_times = 0
        relaunch_times = 0
        while time.time() - start_time < timeout:
            if self.is_weichat_home():
                return True
            if self.is_weichat_login_page():
                raise RuntimeError("微信停留在登录页，请先手动登录后再执行自动化")

            current = self.get_current_activity()
            elapsed = time.time() - start_time
            # 已经不在微信进程里（被按退到桌面），重新拉起
            if current and not current.startswith("com.tencent.mm/"):
                if relaunch_times < 2:
                    logger.info(f"微信已退到后台（前台={current}），重新拉起（第{relaunch_times + 1}次）")
                    try:
                        self.driver.activate_app("com.tencent.mm")
                    except Exception:
                        self.process.execute_shell_output_str("am start -n com.tencent.mm/.ui.LauncherUI")
                    relaunch_times += 1
                    back_times = 0
                    time.sleep(3)
                    continue
            # 微信内但不在首页，返回首页（最多3次，且仅在微信前台时按）
            elif elapsed > 8 and back_times < 3 and current.startswith("com.tencent.mm/"):
                logger.info(f"当前不在微信首页，执行返回（第{back_times + 1}次）")
                self.driver.back()
                back_times += 1
            time.sleep(1)
        return False

    def get_back(self):
        """
        返回上一页
        :return:
        """
        logger.info("点击返回上一页")
        self.driver.back()

    # ==================== 无障碍（TalkBack）开关 ====================
    # 微信 8.0.7x+ 对第三方无障碍服务屏蔽了控件树（page_source 为空、元素找不到），
    # 开启系统读屏服务（TalkBack）后微信会放开无障碍树，元素定位恢复正常。
    TALKBACK_SERVICE = "com.google.android.marvin.talkback/com.google.android.marvin.talkback.TalkBackService"

    def enable_talkback(self):
        """
        description: 开启系统读屏服务，解除微信对无障碍树的屏蔽（幂等，可重复调用）
        """
        current = self.process.execute_shell_output_str("settings get secure enabled_accessibility_services")
        if "talkback" in current.lower():
            logger.info("TalkBack 已开启，跳过")
            return
        logger.info("开启 TalkBack（微信新版本需要读屏服务才能读到控件树）")
        self.process.execute_shell_output_str(f"settings put secure enabled_accessibility_services {self.TALKBACK_SERVICE}")
        self.process.execute_shell_output_str("settings put secure accessibility_enabled 1")
        time.sleep(3)
        # 首次开启会弹出 TalkBack 教程页，先关掉避免挡住后续操作
        current = self.get_current_activity()
        if "talkback" in current.lower() or "accessibility" in current.lower():
            logger.info(f"关闭 TalkBack 教程页：{current}")
            self.process.execute_shell_output_str("input keyevent KEYCODE_BACK")
            time.sleep(1)

    def disable_talkback(self):
        """
        description: 关闭系统读屏服务，恢复手机正常交互（建议在 teardown 中调用）
                     注意用 settings delete 而不是 put ''，避免空字符串被本地 shell 吞掉导致命令失效
        """
        logger.info("关闭 TalkBack")
        self.process.execute_shell_output_str("settings delete secure enabled_accessibility_services")
        self.process.execute_shell_output_str("settings put secure accessibility_enabled 0")
        # 清掉 TalkBack 的任务栈，避免之后出现残留的教程页
        self.process.execute_shell_output_str("am force-stop com.google.android.marvin.talkback")
        time.sleep(1)
        left = self.process.execute_shell_output_str("settings get secure enabled_accessibility_services").strip()
        if left and left != "null":
            logger.warning(f"TalkBack 未完全关闭，当前值：{left}")

    def ensure_weichat_foreground(self):
        """
        description: 确保微信在前台。关闭 TalkBack 后无法再读控件树，
                     所以只能用 activity 判断（adb 方式），不能依赖元素查找
        """
        current = self.get_current_activity()
        if current.startswith("com.tencent.mm/"):
            return True
        logger.info(f"当前前台为 {current}，切回微信")
        try:
            self.driver.activate_app("com.tencent.mm")
        except Exception:
            self.process.execute_shell_output_str("am start -n com.tencent.mm/.ui.LauncherUI")
        time.sleep(2)
        return self.get_current_activity().startswith("com.tencent.mm/")

    def back_to_weichat_home(self, max_back=6):
        """
        description: 从任意页面（内置浏览器/聊天页/设置页）逐级返回微信首页，
                     供串行用例之间还原状态，避免上一个用例的页面深度影响下一个用例
        :param max_back: 最多返回次数，防止死循环
        :return: True 表示已回到微信首页
        """
        # 在 WEBVIEW 上下文里按返回是无效的，先切回原生
        if self.driver.current_context != "NATIVE_APP":
            self.driver.switch_to.context("NATIVE_APP")
            time.sleep(1)
        for i in range(max_back):
            if self.is_weichat_home():
                logger.info("已在微信首页")
                return True
            current = self.get_current_activity()
            if current and not current.startswith("com.tencent.mm/"):
                logger.info(f"已不在微信（前台={current}），重新拉起")
                self.launch_weichat(timeout=30)
                return self.is_weichat_home()
            logger.info(f"返回上一页（{i + 1}/{max_back}），当前页面：{current}")
            self.driver.back()
            time.sleep(1.5)
        return self.is_weichat_home()

    def cleanup_after_test(self, stop_weichat=False, close_talkback=True, back_to_desktop=False):
        """
        description: 用例结束后的状态还原，保证串行用例互不影响、手机可正常使用。
                     执行顺序：退出webview并回到微信首页 -> (可选)关闭微信 -> 关闭TalkBack -> (可选)回桌面
                     注意 close_talkback 必须最后做，关闭后就无法再定位原生元素了
        :param stop_weichat: True 则直接结束微信进程（下个用例冷启动，隔离最彻底，
                             但需要重新开 XWeb 调试，约多花10秒）
        :param close_talkback: True 则关闭读屏服务，恢复手机正常交互
        :param back_to_desktop: True 则最后按 HOME 回到桌面
        :return: True 表示已回到微信首页（stop_weichat=True 时恒为 True）
        """
        ok = True
        if stop_weichat:
            self.force_stop_weichat()
        else:
            try:
                ok = self.back_to_weichat_home()
            except Exception as e:
                logger.error(f"返回微信首页失败：{e}")
                ok = False
        if close_talkback:
            self.disable_talkback()
            # 关闭读屏后系统可能残留 TalkBack 教程/无障碍浮层，只清理这类页面，避免误按返回把微信退掉
            current = self.get_current_activity()
            if "talkback" in current.lower() or "accessibility" in current.lower():
                logger.info(f"清理无障碍残留浮层：{current}")
                self.process.execute_shell_output_str("input keyevent KEYCODE_BACK")
                time.sleep(1)
            self.ensure_weichat_foreground()
        if back_to_desktop:
            self.process.execute_shell_output_str("input keyevent KEYCODE_HOME")
        logger.info(f"用例状态还原完成（回首页={ok}，前台={self.get_current_activity()}）")
        return ok

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
        logger.info(f"通过搜索进入会话：{keyword}")
        # 搜索框：先按 resource-id 找，找不到再按无障碍描述兜底（不同微信版本 id 会变）
        try:
            self.click_weichat_search_box()
        except Exception:
            logger.info("搜索框 id 定位失败，改用 content-desc 定位")
            search_icon = self.assert_util.assert_element_present(
                self.driver,
                (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("搜索")'),
                timeout=5, msg="未找到微信搜索入口")
            search_icon.click()
            time.sleep(1.5)
        edit = self.assert_util.assert_element_present(
            self.driver, (AppiumBy.CLASS_NAME, "android.widget.EditText"),
            timeout=10, msg="未找到微信搜索输入框")
        edit.click()
        edit.clear()
        edit.send_keys(keyword)
        time.sleep(2)
        # 注意：搜索框 EditText 的 text 也是关键词本身，必须限定 TextView 才能命中结果条目
        target = self.assert_util.assert_element_present(
            self.driver,
            (AppiumBy.ANDROID_UIAUTOMATOR,
             f'new UiSelector().text("{keyword}").className("android.widget.TextView")'),
            timeout=10, msg=f"搜索结果中未找到：{keyword}")
        target.click()
        time.sleep(1.5)

    def enter_file_transfer_chat(self):
        """
        description: 进入文件传输助手会话：优先直接点首页会话列表，失败再走搜索
        """
        try:
            row = self.driver.find_element(
                AppiumBy.ANDROID_UIAUTOMATOR,
                'new UiSelector().text("文件传输助手").className("android.widget.TextView")')
            logger.info("从首页会话列表直接点击文件传输助手")
            row.click()
            time.sleep(1.5)
            return
        except Exception:
            logger.info("首页会话列表中未找到，走搜索进入")
        self.enter_chat_by_search("文件传输助手")

    def send_url_in_current_chat(self, url):
        """
        description: 在当前会话输入框输入链接并发送
        :param url: 要发送的链接
        """
        logger.info(f"发送链接：{url}")
        current = self.get_current_activity()
        self.assert_util.assert_true(
            "fts" not in current.lower() and "search" not in current.lower(),
            f"当前仍在搜索页({current})，未进入会话，请检查会话进入逻辑")
        edit = self.assert_util.assert_element_present(
            self.driver, (AppiumBy.CLASS_NAME, "android.widget.EditText"),
            timeout=10, msg="未找到聊天输入框")
        edit.click()
        edit.clear()
        edit.send_keys(url)
        time.sleep(1)
        send_btn = self.assert_util.assert_element_present(
            self.driver,
            (AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().text("发送")'),
            timeout=5, msg="未找到发送按钮")
        send_btn.click()
        time.sleep(2)

    def wait_and_switch_webview(self, timeout=30, process_hint="com.tencent.mm"):
        """
        description: 等待微信内置浏览器加载并切换到 WEBVIEW 上下文
        :param timeout: 等待超时秒数
        :param process_hint: webview 所在进程。注意：新版微信 XWeb 的 webview 跑在主进程
                     com.tencent.mm（旧版才在 :tools），上下文名形如 WEBVIEW_com.tencent.mm
        :return: 切换后的上下文名
        """
        WebDriverWait(self.driver, timeout).until(
            lambda d: any('WEBVIEW' in c for c in d.contexts)
        )
        contexts = self.driver.contexts
        logger.info(f"上下文列表：{contexts}")
        # 只在微信自己的进程里挑，避免误切到系统浏览器等其他应用的 webview
        webviews = [c for c in contexts if c.startswith(f"WEBVIEW_{process_hint}")]
        if not webviews:
            raise RuntimeError(f"未找到微信的 WEBVIEW 上下文（{process_hint}），请确认XWeb调试已开启。当前：{contexts}")
        # 优先精确匹配主进程（新版 XWeb）
        target = f"WEBVIEW_{process_hint}"
        context = target if target in webviews else webviews[0]
        self.driver.switch_to.context(context)
        logger.info(f"已切换到上下文: {context}")
        time.sleep(2)
        return context

    # 内置浏览器加载失败 / 被拦截时出现的页面标题，出现即视为"打开了但页面没出来"
    WEBVIEW_ERROR_TITLES = ("无法打开页面", "网络错误", "页面加载失败", "找不到网页")

    def wait_webview_loaded(self, expect_url=None, timeout=20):
        """
        description: 断言内置浏览器真正加载出目标页面（校验逻辑与失败信息统一在 AssertUtils）
        :param expect_url: 期望 URL 中包含的片段（如域名），None 时只校验是否为 http(s) 页面
        :param timeout: 超时秒数
        :return: 当前页面 URL
        """
        return self.assert_util.assert_page_loaded(
            self.driver,
            expect_url=expect_url,
            error_titles=self.WEBVIEW_ERROR_TITLES,
            timeout=timeout,
            msg=f"{timeout}s 内未加载出目标页面（白名单/网络不通或被拦截时会这样）",
        )

    # XWeb 调试开关页，微信每次进程重启后需要访问一次才能切 WEBVIEW 上下文
    XWEB_DEBUG_URL = "http://debugxweb.qq.com/?inspector=true"

    def _xweb_debug_ready(self):
        """
        description: 检查微信 XWeb 进程是否已开放 webview 调试端口
        :return: True 表示已开放，可以直接切 WEBVIEW
        """
        out = self.process.execute_shell_output_str("cat /proc/net/unix")
        if "webview_devtools_remote_" not in out:
            return False
        ps_out = self.process.execute_shell_output_str("ps -A")
        wx_pids = set()
        for line in ps_out.splitlines():
            if "com.tencent.mm" in line:
                parts = line.split()
                if len(parts) > 1 and parts[1].isdigit():
                    wx_pids.add(parts[1])
        for m in re.finditer(r"webview_devtools_remote_(\d+)", out):
            if m.group(1) in wx_pids:
                return True
        return False

    def ensure_xweb_debug(self):
        """
        description: 确保微信 XWeb 调试开关已开启（冷启动后默认关闭，未开启则切不到 WEBVIEW）
                     调试开关页 debugxweb.qq.com 是微信官方域名，只能通过微信内置浏览器打开，
                     这里借用文件传输助手发一次；该链路仅用于开调试，不再用于打开业务链接
        :return: True 表示调试已开启
        """
        if self._xweb_debug_ready():
            return True
        logger.info("XWeb 调试未开启，先访问 debugxweb.qq.com 开启")
        self.click_home_page_weichat()
        self.enter_file_transfer_chat()
        self._send_and_open_url(self.XWEB_DEBUG_URL, wait_page=6)
        self.driver.back()  # 返回聊天页
        time.sleep(1)
        ready = self._xweb_debug_ready()
        logger.info(f"XWeb 调试开启结果：{ready}")
        return ready

    def _send_and_open_url(self, url, wait_page=6):
        """
        description: 在文件传输助手中发送并点击一个链接（供调试开关和目标链接复用）
        """
        self.send_url_in_current_chat(url)
        msg = self.wait_for_element(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{url}")'), timeout=5)
        if msg is None:
            raise RuntimeError(f"会话中未找到链接消息：{url}")
        logger.info(f"点击链接：{url}")
        msg.click()
        time.sleep(wait_page)

    def open_url_in_wechat(self, url, wait_webview=30, auto_debug=True):
        """
        description: 【已停用】通过文件传输助手发送并点击链接打开网页
                     注意：聊天场景会触发微信外链风控，未备案域名会直接落到拦截页，因此业务入口改用
                     open_fav_in_wechat()（收藏入口）；本方法保留给已备案域名或临时调试使用
        :param url: 目标链接
        :param wait_webview: 等待 webview 出现的超时秒数
        :param auto_debug: 微信进程重启后自动通过 debugxweb.qq.com 开启 webview 调试
        """
        self.click_home_page_weichat()
        self.enter_file_transfer_chat()

        # 冷启动后 XWeb 调试开关是关闭的，先访问一次调试开关页
        if auto_debug:
            self.ensure_xweb_debug()
            self.enter_file_transfer_chat()

        # 会话里已有相同链接消息就直接点，避免每次重复发送
        msg = self.wait_for_element(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{url}")'), timeout=3)
        if msg is None:
            self.send_url_in_current_chat(url)

        msg = self.wait_for_element(
            (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{url}")'), timeout=5)
        if msg is None:
            raise RuntimeError(f"会话中未找到链接消息：{url}")
        logger.info("点击目标链接消息")
        msg.click()
        time.sleep(2)
        self.wait_and_switch_webview(timeout=wait_webview)

    def open_fav_in_wechat(self, title, wait_webview=30, expect_url=None):
        """
        description: 从「我 -> 收藏」打开指定标题的收藏链接并切换到 WEBVIEW 上下文
                     说明：聊天消息里的链接会触发微信外链风控预检（未备案域名直接出拦截页），
                     而收藏入口不做该预检，可直接请求目标域名，适合被拦域名的自动化入口
        :param title: 收藏条目的标题文本（如 "测试环境首页"）
        :param wait_webview: 等待 webview 出现的超时秒数
        :param expect_url: 期望 URL 包含的片段，用于确认加载的是目标页而不是错误页
        """
        self.click_home_page_weichat()
        # 冷启动后 XWeb 调试是关的，切不到 WEBVIEW，先确保开启
        self.ensure_xweb_debug()
        me_tab = self.assert_util.assert_native_text_present(
            self.driver, "我", msg="未找到底部「我」标签")
        me_tab.click()
        time.sleep(1.5)
        fav_entry = self.assert_util.assert_native_text_present(
            self.driver, "收藏", msg="未找到「收藏」入口")
        fav_entry.click()
        time.sleep(2)
        item = self.assert_util.assert_native_text_present(
            self.driver, title, msg=f"收藏列表中未找到：{title}")
        logger.info(f"从收藏打开：{title}")
        item.click()
        time.sleep(2)
        self.wait_and_switch_webview(timeout=wait_webview)
        return self.wait_webview_loaded(expect_url=expect_url)
