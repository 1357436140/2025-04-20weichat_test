# -*- coding: utf-8 -*-
import time

# @author: Jason
# @File: test_code_demo.py
# @Time: 4月 20, 2025
# @description:
from common.base_test import BaseTest
from common.logger import get_logger
from utils.weichat_utils import WeichatUtils

logger = get_logger()

# 测试总链对应的收藏标题（微信聊天入口会被外链风控拦截，统一走「我 -> 收藏」入口）
FAV_TITLE = "测试环境首页"
# 用于确认加载的是目标域名，而不是微信错误页/拦截页
EXPECT_URL = "uatxyk.cibfintech.com"


class TestWeichat(BaseTest):

    def setup_method(self, method):
        super().setup_method(method)
        self.weichat_util = WeichatUtils()

    def test_demo_01(self):
        # 冷启动微信 -> 从收藏打开测试总链（内部已切到 WEBVIEW，并断言页面真的加载出来）
        self.weichat_util.launch_weichat()
        self.weichat_util.open_fav_in_wechat(FAV_TITLE, expect_url=EXPECT_URL)
        # H5 业务操作：每一步内部都调用了断言（见 common/assert_utils.py），失败直接抛 AssertionError
        self.weichat_util.click_link_sit()
        self.weichat_util.click_link_weixin()
        self.weichat_util.click_link_title('1、账单查询')
        # 账单页全要素检查：校验稳定结构与文案，还款状态/金额/日期/版本号只采集不断言
        self.weichat_util.check_bill_page()

    def teardown_method(self):
        super().teardown()
        # 还原现场：退出 webview、回到微信首页、关闭 TalkBack，保证下个用例从干净状态开始
        # 用例污染较重时可改为 cleanup_after_test(stop_weichat=True) 彻底冷启动
        self.weichat_util.cleanup_after_test(stop_weichat=False, close_talkback=True)
        self.weichat_util.driver.quit()
