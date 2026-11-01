# -*- coding: utf-8 -*-

# @author: Jason
# @File: demo_open_test_url.py
# @Time: 2026-11-01
# @description: 示例：冷启动微信 -> 在微信内置浏览器打开测试总链 -> 切到 WEBVIEW 上下文 -> 用例结束还原现场
import sys
import time

from common.logger import get_logger
from utils.weichat_utils import WeichatUtils

logger = get_logger()

# 测试总链，可用命令行第一个参数覆盖：python demo_open_test_url.py <url>
TARGET_URL = "https://uatxyk.cibfintech.com/html/webapp/new_test/index.html"
# 收藏入口使用的收藏标题（提前在微信里收藏一次目标链接；聊天入口对未备案域名会被微信拦截）
FAV_TITLE = "测试环境首页"


def main(url=TARGET_URL):
    logger.info("=" * 60)
    logger.info(f"示例开始，目标链接：{url}")
    logger.info("=" * 60)

    weichat = WeichatUtils()  # 创建 Appium 会话（同时会拉起微信）
    try:
        # 1. 冷启动微信，等待主界面就绪
        weichat.launch_weichat(restart=True)

        # 2. 从「我 -> 收藏」打开测试总链（聊天入口会被微信外链风控拦截，收藏入口不受影响），
        #    并切换到 WEBVIEW 上下文
        weichat.open_fav_in_wechat(FAV_TITLE)

        logger.info(f"当前前台页面：{weichat.get_current_activity()}")
        logger.info(f"当前上下文名称：{weichat.driver.current_context}")
        time.sleep(2)
    finally:
        # 3. 用例结束还原现场：回到微信首页 + 关闭 TalkBack，避免影响下个用例和手机正常使用
        weichat.cleanup_after_test(stop_weichat=False, close_talkback=True, back_to_desktop=False)
        weichat.driver.quit()


if __name__ == "__main__":
    target_url = sys.argv[1] if len(sys.argv) > 1 else TARGET_URL
    main(target_url)
