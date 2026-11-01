# 微信 H5 自动化测试框架（weichat_test）

> **最后更新时间**：2026-11-01 22:25
> **当前版本**：v1.0.0
> **维护约定**：每次代码变更同步更新本文档，并在开头刷新"最后更新时间/当前版本"，同时在第 8 节追加更新日志。

面向「微信内置浏览器 H5」的 UI 自动化测试框架，基于 **Appium 2 + UiAutomator2** 驱动真机微信，打通了从**冷启动微信 → 进入指定入口 → 打开 H5 → 切换 WEBVIEW 上下文 → 执行业务断言 → 还原现场**的完整链路，并针对微信 8.0.7x+ 的反自动化、外链风控、XWeb 调试等实际障碍做了工程化封装。

---

## 1. 项目简介

| 项目 | 说明 |
|---|---|
| 项目定位 | 微信内嵌 H5（如信用卡账单类 WebApp）的端到端自动化测试 |
| 目标应用 | 微信 Android 版（实测 8.0.79） |
| 驱动方式 | Appium 2 server + UiAutomator2 driver + Appium-Python-Client |
| 被测环境 | `https://uatxyk.cibfintech.com/html/webapp/new_test/index.html`（UAT） |
| 测试框架 | pytest（用例继承 `common/base_test.py::BaseTest`） |
| 运行平台 | macOS + 真机（adb 连接），实测机型 Redmi `22041211AC` / Android 14 |

核心设计目标：

1. **能点得动**——解决微信屏蔽第三方无障碍服务导致的"元素读不到"问题；
2. **能进得去**——解决微信外链风控导致的"链接被拦成二维码复制页"问题；
3. **能断得准**——真机 WEBVIEW 上下文切换 + chromedriver 对接 XWeb，支持 H5 DOM 断言；
4. **能串得住**——每个用例前后自动还原现场（回微信首页、关闭 TalkBack），保证串行用例互不干扰。

---

## 2. 技术栈与运行环境

| 组件 | 版本（实测） | 说明 |
|---|---|---|
| Python | 3.10.11 | 项目解释器（macOS Framework 版） |
| Appium server | 3.8.0 | `appium --port 4723`，Appium 2 架构 |
| appium driver | uiautomator2 | `appium driver list --installed` 确认已装 |
| Appium-Python-Client | 6.0.7 | 使用 `UiAutomator2Options` 加载 caps |
| selenium | 4.50.0 | 提供 WebDriverWait / EC 等 |
| adbutils | 2.12.0 | 设备序列号、系统版本获取 |
| pytest | 9.1.1 | 用例执行 |
| chromedriver | 150（随仓库 `common/tools/chromedriver`） | 与设备 XWeb 内核版本匹配，`.gitignore` 已排除不入库 |
| 设备 | Redmi 22041211AC / Android 14 | 微信 8.0.79，User 版本（**未 root**） |

> 依赖安装（参考）：
> ```bash
> pip install Appium-Python-Client==6.0.7 selenium==4.50.0 adbutils==2.12.0 pytest==9.1.1
> appium driver install uiautomator2
> ```

---

## 3. 目录结构

```
2025-04-20weichat_test/
├── confest.py                      # pytest 配置占位（当前为空壳）
├── common/                         # 公共基础层
│   ├── base_test.py                # 用例基类 BaseTest（setup/teardown 钩子）
│   ├── driver.py                   # Appium 会话工厂（Mac 版，当前使用）
│   ├── driver2.py                  # 备用驱动实现
│   ├── exec_cmd.py                 # ExecuteCommand：adb / shell / 本地命令执行封装
│   ├── find_ui.py                  # 元素定位工具（resource-id / text / xpath）
│   ├── functions.py                # 设备信息、亮屏等辅助函数
│   ├── global_attrs.py             # 全局路径常量（chromedriver 路径等）
│   ├── logger.py                   # 日志封装 + get_logger() 单例
│   ├── paths.py                    # 路径常量（占位）
│   ├── decorators.py               # 装饰器（占位）
│   └── watchers.py                 # 系统弹窗监听词表（Watchers_chinese / LqWatcher）
├── utils/
│   └── weichat_utils.py            # 微信业务操作核心类 WeichatUtils（本项目核心）
├── scripts/
│   └── redmi_note_11pro/           # 按机型/设备划分的用例目录
│       ├── demo_open_test_url.py   # 演示脚本：冷启动 → 收藏入口打开总链 → 切 WEBVIEW → 还原
│       └── test_code_demo.py       # pytest 用例示例（账单查询流程）
├── logs/
│   ├── scripts_logs/run.log        # 运行日志（已 gitignore）
│   └── screenshots/                # 失败截图目录
└── reports/                        # 测试报告输出目录
```

---

## 4. 核心能力（微信自动化的关键链路）

### 4.1 启动与会话管理

`WeichatUtils.launch_weichat(timeout=30, restart=False, unlock=True)`

1. 唤醒屏幕（`keyevent 224`）+ 解除无密码锁屏（`keyevent 82`），避免"启动成功却停在锁屏"；
2. `restart=True` 时先 `am force-stop com.tencent.mm` 冷启动，保证干净首屏；
3. 已在前台则不重复拉起；否则优先 `driver.activate_app()`，失败回退 `am start -n com.tencent.mm/.ui.LauncherUI`；
4. 轮询底部「通讯录」tab 出现才算就绪；若微信恢复到聊天子页会自动 `back` 回首页，检测到登录页则直接报错提示先手工登录。

配套：`force_stop_weichat()`、`get_current_activity()`（解析 dumpsys 拿前台页面）、`wait_weichat_home()`、`is_weichat_home()`、`is_weichat_login_page()`。

### 4.2 无障碍：微信屏蔽控件树的对策（TalkBack）

微信 8.0.79 对**第三方无障碍服务**隐藏了控件树：同期对照实验里 MIUI 桌面能拿到 88KB 层级，微信首页 `page_source` 只有空节点（`a11y-important=false`），`text("通讯录")` 必然定位失败。

**解法**：自动化前开启系统 **TalkBack**（微信对系统读屏放开无障碍树）。实测开启后 `page_source` 达 110KB，文本定位恢复正常；点击等操作仍然有效。

- `enable_talkback()` / `disable_talkback()`：`launch_weichat` 内部自动开启；
- 关闭时必须用 `settings delete secure enabled_accessibility_services`——写成 `settings put ... ''` 时空引号会被本地 shell 吞掉，导致**静默失效**（现场表现为"跑完手机停在 TalkBack 教程页"）；
- 关闭后顺带结束 TalkBack 进程清理其任务栈。

### 4.3 打开 H5 的入口选择（重要）

微信外链风控**按入口（场景值）分级**，同一 URL 不同入口结果不同（实机对比所得）：

| 入口 | 表现 | 是否可用 |
|---|---|---|
| 聊天消息 / 文件传输助手 | 命中微信拦截页，DOM `data-module="urlweb"`，文案"如需浏览，请长按网址复制后使用浏览器访问"，**请求根本不发出** | ❌ |
| 我 → 收藏 → 条目 | 前台 `MMWebViewUI`，地址栏正常显示目标域名并发起请求 | ✅ |

因此业务入口统一走 **收藏**：`open_fav_in_wechat(title)`。

- 需提前在微信里**收藏一次**目标链接，把标题传给方法（默认 `测试环境首页`）；
- 收藏入口不做消息层的链接安全预检，因此未备案域名也能直接请求（页面能否加载取决于服务端 IP 白名单）；
- 聊天入口方法 `open_url_in_wechat(url)` 已标记**停用并保留**，仅用于已备案域名或临时调试。

> 备选入口：扫一扫（生成二维码 → 推入相册 → 扫一扫识别）通常也不受聊天风控限制，且可参数化任意 URL，需要时可再封装。

### 4.4 XWeb 调试与 WEBVIEW 上下文切换

- 微信 webview 的调试端口**必须开启**才能切上下文：冷启动后默认关闭，需在内置浏览器访问一次 `http://debugxweb.qq.com/?inspector=true`；
  `ensure_xweb_debug()` 会先探测 `webview_devtools_remote_<pid>` 是否属于微信进程，未开启则自动通过文件传输助手打开该开关页（这是聊天链路唯一保留的用途）。
- 新版微信（8.0.7x+）XWeb 跑在**主进程**，上下文名为 `WEBVIEW_com.tencent.mm`；旧版才是 `com.tencent.mm:tools`。`driver.py` 的 `chromeOptions.androidProcess` 已同步为 `com.tencent.mm`。
- 上下文选择逻辑会校验进程归属，避免误切到系统浏览器（`WEBVIEW_com.android.browser`）——否则 chromedriver 连的是别的页面的调试端口，表现为"切换成功但断言全挂"。

### 4.5 用例隔离与现场还原

`cleanup_after_test(stop_weichat=False, close_talkback=True, back_to_desktop=False)`

- 默认：切回 `NATIVE_APP` → 逐级返回（内置浏览器 → 聊天/收藏页 → 首页，实测 2~3 次 `back`）→ 关闭 TalkBack → 可选回桌面；
- `stop_weichat=True`：直接结束微信进程，隔离最彻底，代价是下次冷启动需重开 XWeb 调试（约多 10 秒）；
- 目的是让**串行用例**互不干扰：上一条用例深入到多层级页面后，下一条仍从首页开始。

---

## 5. 快速开始

### 5.1 环境准备

```bash
# 1) 启动 Appium（Appium 2，注意地址不要带 /wd/hub）
appium --port 4723

# 2) 确认设备在线
adb devices

# 3) 首次运行需给 Appium 辅助应用授权（MIUI 上缺定位权限会导致会话创建失败：
#    "Appium Settings app is not running"）
adb shell pm grant io.appium.settings android.permission.ACCESS_FINE_LOCATION
adb shell pm grant io.appium.settings android.permission.ACCESS_COARSE_LOCATION
adb shell pm grant io.appium.settings android.permission.FOREGROUND_SERVICE_LOCATION
```

### 5.2 运行演示脚本

```bash
cd /Users/hanguang/PycharmProjects/2025-04-20weichat_test
env -u HTTP_PROXY -u HTTPS_PROXY -u http_proxy -u https_proxy -u ALL_PROXY -u all_proxy \
  PYTHONPATH=$PWD \
  /Library/Frameworks/Python.framework/Versions/3.10/bin/python3 \
  scripts/redmi_note_11pro/demo_open_test_url.py
```

预期日志：

```
微信启动完成，已进入主界面
从收藏打开：测试环境首页
已切换到上下文: WEBVIEW_com.tencent.mm
当前前台页面：com.tencent.mm/.plugin.webview.ui.tools.MMWebViewUI
用例状态还原完成（回首页=True，前台=com.tencent.mm/.ui.LauncherUI）
```

### 5.3 运行 pytest 用例

```bash
env -u http_proxy -u https_proxy PYTHONPATH=$PWD \
  /Library/Frameworks/Python.framework/Versions/3.10/bin/python3 -m pytest \
  scripts/redmi_note_11pro/test_code_demo.py -s
```

---

## 6. 常用 API（`utils/weichat_utils.py`）

### 会话与启动

| 方法 | 说明 |
|---|---|
| `launch_weichat(timeout=30, restart=False, unlock=True)` | 唤醒 → 启动 → 等待主界面就绪（自动开 TalkBack） |
| `force_stop_weichat()` | 结束微信进程 |
| `get_current_activity()` | 取前台 Activity（如 `com.tencent.mm/.ui.LauncherUI`） |
| `wait_weichat_home()` / `is_weichat_home()` / `is_weichat_login_page()` | 首页/登录页判定 |

### 入口与页面

| 方法 | 说明 |
|---|---|
| `open_fav_in_wechat(title)` | **推荐入口**：我 → 收藏 → 点标题 → 切 WEBVIEW |
| `open_url_in_wechat(url)` | 【已停用】文件传输助手发链接再点击（受外链风控限制） |
| `ensure_xweb_debug()` | 确保 XWeb 调试开关已开启 |
| `wait_and_switch_webview(timeout=30)` | 等待并切到微信 webview 上下文 |
| `enter_chat_by_search(keyword)` / `enter_file_transfer_chat()` | 通过搜索进入指定会话 |
| `send_url_in_current_chat(url)` | 在当前会话发送文本/链接 |

### 还原与工具

| 方法 | 说明 |
|---|---|
| `cleanup_after_test(...)` | 现场还原：回首页 + 关 TalkBack + 可选结束微信/回桌面 |
| `back_to_weichat_home(max_back=6)` | 逐级返回微信首页 |
| `enable_talkback()` / `disable_talkback()` | 读屏服务开关 |
| `wait_for_element(locator, timeout)` | 显式等待元素（返回 None 而非抛异常） |

---

## 7. 常见问题与坑点

1. **元素读不到 / `page_source` 为空**：微信屏蔽第三方无障碍，先开 TalkBack（`launch_weichat` 已内置）。
2. **链接被拦成"长按网址复制"页**：聊天入口触发外链风控，改用收藏入口；根治办法是配置公众号「业务域名」或完成 ICP 备案。
3. **切上下文报 chromedriver 连接失败**：冷启动后 XWeb 调试未开（`ensure_xweb_debug()`），或 `androidProcess` 仍写成 `:tools`（新版微信在主进程）。
4. **会话创建失败 `Appium Settings app is not running`**：`io.appium.settings` 缺定位权限而崩溃，按 5.1 授权。
5. **客户端连不上 `127.0.0.1:4723`**：本机代理环境变量拦截，命令前加 `env -u http_proxy -u https_proxy ...`。
6. **`ExecuteCommand.execute_shell*` 里的管道/引号失效**：底层用 `shell=True` 拼命令，`|`、`''` 会被本地 shell 吃掉；需要解析输出时改为"整段取回 + Python 正则"，需要空值时用 `settings delete`。
7. **`Logger.info()` 只接受一个参数**：多参数必须用 f-string 拼接，否则运行时 `TypeError`。
8. **`uiautomator dump` 在微信上返回空层级**：CLI 工具局限，Appium 的 UiAutomator2 instrumentation 不受影响。
9. **日志与驱动文件不入库**：`logs/**/*.log`、`common/tools/chromedriver` 已在 `.gitignore` 中排除。

---

## 8. 版本与更新日志

> 维护约定：每次改动代码/文档后，①刷新文首"最后更新时间 + 当前版本"；②在本节追加一条记录（版本 / 日期 / 变更摘要）。

| 版本 | 日期 | 变更摘要 |
|---|---|---|
| v1.0.0 | 2026-11-01 | 首个完整文档版本：`open_fav_in_wechat` 收藏入口、`ensure_xweb_debug` 调试自开、`cleanup_after_test` 现场还原、全项目 print→logger、`.gitignore` 修正 |
| v0.9.0 | 2026-11-01 | 打通端到端链路：TalkBack 放开无障碍、会话进入与发链接、WEBVIEW 上下文修正（主进程 `com.tencent.mm`）、XWeb 调试自动开启 |
| v0.1.0 | 2025-04-20 | 项目骨架：Appium 会话工厂、命令执行封装、元素定位工具、日志与基础用例结构 |

---

## 9. 待办 / 后续规划

- [ ] 服务端 IP 白名单放通后，补充首页加载成功断言（当前仅验证到"发起请求 + 进入 MMWebViewUI"）；
- [ ] 封装「扫一扫」入口，支持任意 URL 参数化打开；
- [ ] 引入 `reports/` HTML 报告与失败自动截图；
- [ ] 清理 `weichat_utils.py` 中已被 `wait_and_switch_webview()` 取代的旧方法（`switch_content` / `wait_for_content` / `click_test_link` 等）。
