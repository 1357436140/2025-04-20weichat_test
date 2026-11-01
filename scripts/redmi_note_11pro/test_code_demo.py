# -*- coding: utf-8 -*-
import time

# @author: Jason
# @File: test_code_demo.py
# @Time: 4月 20, 2025
# @description:
from common.base_test import BaseTest
from utils.weichat_utils import WeichatUtils


class TestWeichat(BaseTest):

    def setup_method(self, method):
        super().setup_method(method)
        self.weichat_util = WeichatUtils()

    def test_demo_01(self):
        self.weichat_util.launch_weichat()
        self.weichat_util.wait_for_content()
        self.weichat_util.switch_content()
        self.weichat_util.click_link_sit()
        self.weichat_util.click_link_weixin()
        self.weichat_util.click_link_title('1、账单查询')
        self.weichat_util.check_zhangdan_exit()

    def teardown_method(self):
        super().teardown()
        self.weichat_util.get_back()
        self.weichat_util.force_stop_weichat()



