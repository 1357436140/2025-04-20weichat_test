# -*- coding: utf-8 -*-

# @author: Jason
# @File: assert_utils.py
# @Time: 2026-11-03
# @description: 断言封装。所有 UI 校验集中在这里，业务方法内部调用并返回结果，
#               测试函数只做流程编排，不再散落 assert。
import re
import time

from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.wait import WebDriverWait

from common.logger import get_logger

logger = get_logger()


class AssertUtils:
    """
    UI 断言集合：
    - 断言失败统一抛 AssertionError（pytest 会直接标记用例失败，并带上自定义信息）
    - 断言通过返回实际值，方便业务方法继续复用（如断言元素存在后直接点击）
    """

    # H5 页面（Vue 应用）常用的两种文本定位
    XPATH_SPAN_TEXT = '//span[contains(normalize-space(.),"{}")]'
    XPATH_A_TEXT = '//a[contains(normalize-space(.),"{}")]'
    # 内置浏览器/网关打不开页面时的标题关键字，命中即视为"页面没出来"
    # 注意：网关错误页的 readyState 同样是 complete，只靠 readyState 会假通过
    DEFAULT_ERROR_TITLES = (
        "无法打开页面", "网络错误", "页面加载失败", "找不到网页",
        "网关错误", "502", "503", "504", "Bad Gateway", "Service Unavailable",
        "该网页无法正常运作", "页面不存在", "访问受限",
    )

    # ==================== 基础断言 ====================

    def assert_true(self, condition, msg=""):
        """
        description: 布尔断言
        :param condition: 待判断的条件
        :param msg: 失败信息
        :return: condition
        """
        assert condition, msg or f"断言失败，实际值：{condition}"
        logger.info("断言通过｜条件成立")
        return condition

    def assert_equal(self, actual, expected, msg=""):
        """
        description: 相等断言
        :param actual: 实际值
        :param expected: 期望值
        :param msg: 失败信息
        :return: actual
        """
        assert actual == expected, msg or f"断言失败，期望：{expected}，实际：{actual}"
        logger.info(f"断言通过｜{msg or f'{actual} == {expected}'}")
        return actual

    # ==================== 元素断言 ====================

    def assert_element_present(self, driver, locator, timeout=10, msg=""):
        """
        description: 断言元素存在，返回元素对象（便于直接点击/取值）
        :param driver: WebDriver
        :param locator: 定位元组，如 (AppiumBy.XPATH, '//span[contains(.,"sit")]')
        :param timeout: 等待超时秒数
        :param msg: 失败信息
        :return: WebElement
        """
        try:
            element = WebDriverWait(driver, timeout, 1).until(lambda d: d.find_element(*locator))
        except Exception:
            element = None
        if element is None:
            raise AssertionError(msg or f"元素未出现：{locator[1]}")
        logger.info(f"断言通过｜元素存在：{str(locator[1])[:60]}")
        return element

    def assert_span_text_present(self, driver, text, timeout=10, msg=""):
        """断言页面存在指定文本的 span 元素（H5 常用），返回元素"""
        return self.assert_element_present(
            driver, (AppiumBy.XPATH, self.XPATH_SPAN_TEXT.format(text)), timeout,
            msg or f"页面未出现文本「{text}」")

    def assert_a_text_present(self, driver, text, timeout=10, msg=""):
        """断言页面存在指定文本的 a 标签元素（H5 链接/按钮），返回元素"""
        return self.assert_element_present(
            driver, (AppiumBy.XPATH, self.XPATH_A_TEXT.format(text)), timeout,
            msg or f"页面未出现链接「{text}」")

    def assert_native_text_present(self, driver, text, timeout=10, msg=""):
        """断言原生页面存在指定 text 的控件（UiAutomator），返回元素"""
        return self.assert_element_present(
            driver, (AppiumBy.ANDROID_UIAUTOMATOR, f'new UiSelector().text("{text}")'), timeout,
            msg or f"原生页面未出现控件「{text}」")

    def assert_text_present(self, driver, text, timeout=10, msg=""):
        """断言页面存在指定文本节点（任意标签：p/span/div/i 等），返回元素"""
        return self.assert_element_present(
            driver,
            (AppiumBy.XPATH, f'//*[contains(normalize-space(text()),"{text}")]'),
            timeout, msg or f"页面未出现文本「{text}」")

    def assert_css_present(self, driver, css_selector, timeout=10, msg=""):
        """
        description: 断言存在匹配 CSS 选择器的元素（适合无文字的组件，如图片印章）
        :return: True
        """
        end_time = time.time() + timeout
        while time.time() < end_time:
            try:
                found = driver.execute_script(
                    "return document.querySelector(arguments[0]) !== null;", css_selector)
            except Exception:
                found = False
            if found:
                logger.info(f"断言通过｜元素存在：css={css_selector}")
                return True
            time.sleep(1)
        raise AssertionError(msg or f"{timeout}s 内未找到元素：css={css_selector}")

    def assert_body_text_matches(self, driver, pattern, timeout=10, msg=""):
        """
        description: 断言页面正文匹配正则（用于金额、日期、版本号等动态文本），返回匹配到的内容
        """
        end_time = time.time() + timeout
        last_body = ""
        while time.time() < end_time:
            try:
                body = driver.execute_script("return document.body.innerText;") or ""
            except Exception:
                body = ""
            last_body = body
            m = re.search(pattern, body)
            if m:
                logger.info(f"断言通过｜正文匹配 /{pattern}/ -> {m.group(0)}")
                return m.group(0)
            time.sleep(1)
        raise AssertionError(
            msg or f"{timeout}s 内正文未匹配 /{pattern}/，页面文本前200字：{last_body[:200]}")

    def assert_text_count_at_least(self, driver, text, at_least, timeout=10, msg=""):
        """
        description: 断言指定完整文本的叶子元素数量不少于 at_least（如账单页应有2个「查账」入口）
        :return: 实际数量
        """
        end_time = time.time() + timeout
        count = 0
        while time.time() < end_time:
            try:
                count = driver.execute_script(
                    'return [...document.querySelectorAll("span,a,p,div,button,i")]'
                    '.filter(e => e.childElementCount === 0 '
                    '&& (e.innerText||"").trim() === arguments[0]).length;', text)
            except Exception:
                count = 0
            if count >= at_least:
                logger.info(f"断言通过｜「{text}」出现 {count} 次（要求 ≥{at_least}）")
                return count
            time.sleep(1)
        raise AssertionError(msg or f"「{text}」出现 {count} 次，少于要求的 {at_least} 次")

    # ==================== 页面断言 ====================

    def match_error_title(self, title, error_titles=None):
        """
        description: 标题是否命中错误页关键字（包含匹配，兼容"502 网关错误"这类带前缀的标题）
        :param title: 页面标题
        :param error_titles: 关键字集合，默认取 DEFAULT_ERROR_TITLES
        :return: 命中的关键字；未命中返回 None
        """
        text = (title or "").strip().lower()
        for keyword in (error_titles or self.DEFAULT_ERROR_TITLES):
            if keyword.lower() in text:
                return keyword
        return None

    def assert_page_loaded(self, driver, expect_url=None, error_titles=None, timeout=20, msg=""):
        """
        description: 断言内置浏览器真的加载出目标页面（排除微信错误页/网关错误页）
                     判定条件：URL 为 http(s) + 期望片段命中 + 标题不命中错误页关键字 + readyState=complete
                     注意：网关错误页（如 502）的 readyState 同样是 complete，只判断 readyState 会假通过
        :param driver: WebDriver（需已切到 WEBVIEW 上下文）
        :param expect_url: 期望 URL 包含的片段（如域名），None 则只校验协议
        :param error_titles: 错误页标题关键字集合，默认取 DEFAULT_ERROR_TITLES
        :param timeout: 超时秒数
        :param msg: 失败信息
        :return: 当前 URL
        """
        titles = error_titles or self.DEFAULT_ERROR_TITLES
        start_time = time.time()
        last_state = ""
        while time.time() - start_time < timeout:
            try:
                url = driver.current_url or ""
                title = driver.title or ""
                ready = driver.execute_script("return document.readyState")
            except Exception as e:
                last_state = f"读取页面状态失败：{e}"
                time.sleep(1)
                continue
            hit = self.match_error_title(title, titles)
            last_state = f"url={url} title={title} readyState={ready}"
            if hit:
                last_state = f"{last_state}（命中错误页关键字「{hit}」）"
                logger.warning(f"页面是错误页：{last_state}")
            elif (url.startswith("http")
                    and (expect_url is None or expect_url in url)
                    and ready == "complete"):
                logger.info(f"断言通过｜页面已加载：{last_state}")
                return url
            time.sleep(1)
        raise AssertionError(msg or f"{timeout}s 内未加载出目标页面，最后状态：{last_state}")

    def assert_page_title_contains(self, driver, keyword, msg=""):
        """断言当前页面标题包含关键字，返回标题"""
        title = driver.title or ""
        assert keyword in title, msg or f"页面标题不含「{keyword}」，实际标题：{title}"
        logger.info(f"断言通过｜标题包含「{keyword}」")
        return title

    def assert_url_contains(self, driver, fragment, msg=""):
        """断言当前 URL 包含指定片段（如路由 /billMain），返回 URL"""
        url = driver.current_url or ""
        assert fragment in url, msg or f"URL 不含「{fragment}」，实际：{url}"
        logger.info(f"断言通过｜URL 包含「{fragment}」")
        return url
