# 微信 H5 自动化测试框架（weichat_test）

> **最后更新时间**：2026-11-03 20:35
> **当前版本**：v1.4.0
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
│   ├── assert_utils.py             # AssertUtils：断言统一入口（元素/页面/布尔/相等）
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

因此业务入口统一走 **收藏**：`open_fav_in_wechat(title, expect_url=...)`。

- 需提前在微信里**收藏一次**目标链接，把标题传给方法（默认 `测试环境首页`）；
- 收藏入口不做消息层的链接安全预检，因此未备案域名也能直接请求（页面能否加载取决于服务端 IP 白名单）；
- 方法内部会调用 `wait_webview_loaded()` 校验"页面真的加载出来了"：URL 必须是 http(s)、标题不在错误页名单（`无法打开页面` 等）、`document.readyState == complete`，任一不满足直接抛异常，避免页面没打开用例却继续往下跑的**假通过**；
- 聊天入口方法 `open_url_in_wechat(url)` 已标记**停用并保留**，仅用于已备案域名或临时调试。

> 备选入口：扫一扫（生成二维码 → 推入相册 → 扫一扫识别）通常也不受聊天风控限制，且可参数化任意 URL，需要时可再封装。

### 4.4 XWeb 调试与 WEBVIEW 上下文切换

- 微信 webview 的调试端口**必须开启**才能切上下文：冷启动后默认关闭，需在内置浏览器访问一次 `http://debugxweb.qq.com/?inspector=true`；
  `ensure_xweb_debug()` 会先探测 `webview_devtools_remote_<pid>` 是否属于微信进程，未开启则自动通过文件传输助手打开该开关页（这是聊天链路唯一保留的用途）。
- 新版微信（8.0.7x+）XWeb 跑在**主进程**，上下文名为 `WEBVIEW_com.tencent.mm`；旧版才是 `com.tencent.mm:tools`。`driver.py` 的 `chromeOptions.androidProcess` 已同步为 `com.tencent.mm`。
- 上下文选择逻辑会校验进程归属，避免误切到系统浏览器（`WEBVIEW_com.android.browser`）——否则 chromedriver 连的是别的页面的调试端口，表现为"切换成功但断言全挂"。

### 4.5 用例隔离与现场还原

`cleanup_after_test(stop_weichat=False, close_talkback=True, back_to_desktop=False)`

- 默认：切回 `NATIVE_APP` → 逐级返回 → 关闭 TalkBack → 可选回桌面。返回次数与页面深度有关：浅层（收藏列表 → H5 → 收藏列表）**2~3 次** `back` 即可；账单页这种深层实测要 **5 次**（4 次在 WebView 里退 H5 路由，第 5 次才关掉页面/退出收藏列表）；
- 返回判定用 **activity（`LauncherUI`）** 而不是找「通讯录」文本：H5 页里永远找不到该文本，每次 `find_element` 都要等 UiAutomator2 超时（实测 ~10s），5 层页面会直接撞满 `max_back` 预算；
- 卡住兜底：连续两次 `back` 后 activity 没变化（被 WebView 历史吃掉），改用 `am start … --activity-clear-top` 清任务栈；仍失败则冷启动。`cleanup_after_test` 拿不到 `True` 时还会再兜一层冷启动；
- 口径提醒：回到的是 `LauncherUI`，可能停在「微信/通讯录/发现/我」任一 tab（实测账单页退回来落在「我」tab），**不等于聊天列表**；下个用例由 `launch_weichat()` 统一拉正；
- `stop_weichat=True`：直接结束微信进程，隔离最彻底，代价是下次冷启动需重开 XWeb 调试（约多 10 秒）；
- 目的是让**串行用例**互不干扰：上一条用例深入到多层级页面后，下一条仍从首页开始。

典型返回链路（2026-11-03 日志实测）：

| 次序 | `back` 前所在页面 | 实际动作 |
|---|---|---|
| 1–3 | `MMWebViewUI`（账单查询 → 微信总链 → 测试环境首页） | H5 内路由后退，activity 不变 |
| 4 | `MMWebViewUI`（H5 首层） | 关闭 WebView，落到 `FavoriteIndexUI` |
| 5 | `FavoriteIndexUI` | 退到 `LauncherUI`（「我」tab），判定命中停止 |

### 4.6 断言分层：断言不进测试函数

为保证"测试函数只描述流程、断言集中管理"，项目做了三层分工：

| 层 | 文件 | 职责 |
|---|---|---|
| 断言层 | `common/assert_utils.py` | `AssertUtils` 统一实现元素存在、页面加载、布尔/相等断言；失败抛 `AssertionError` 并带上下文信息 |
| 业务层 | `utils/weichat_utils.py` | 公共方法内部**调用断言**再执行动作，并向调用方**返回结果**（如 `click_link_sit()` → 断言 sit 入口存在 → 点击 → 返回 `True`） |
| 用例层 | `scripts/**/test_*.py` | 只编排流程，**不写 assert**：`open_fav_in_wechat → click_link_sit → click_link_weixin → click_link_title → check_bill_page` |

好处：断言消息只有一处维护；页面没加载/元素没出现时，失败信息直接指向具体步骤（如"总链首页未出现「sit」环境入口"），而不是笼统的 `AssertionError`；后续新增用例不必重复写断言。

### 4.7 账单页检查策略：只断言"稳定的东西"

`check_bill_page()` 对账单查询页做全要素检查，但**刻意把会随账务变化的内容排除在断言之外**——否则每月账单状态一变，用例就红。

| 纳入断言（结构与固定文案） | 只采集不断言（会变化） |
|---|---|
| 路由 `/billMain`、标题「账单查询」 | 还款状态章（已还清/未还清/逾期，印章还是图片） |
| 「切换卡片」入口、卡号后四位格式 `(\d{4})` | 各金额数值（剩余应还/账单金额/可用额度/未出账单） |
| 区块标题：本期账单、未出账单 | 未出账单的出账日期（如「11月15日出账」） |
| 字段标签：剩余应还、剩余最低还款、账单金额、可用额度 | 营销角标文案（如「跨行还款0手续费」「推荐」） |
| 「查账」入口数量 ≥2（本期 + 未出各一） | 页脚版本号（随发布变化） |
| 按钮：还款、分期还款；入口：历史账单、现金分期、预借现金 | 环境标识（sit/uat，随环境变化） |
| 页脚版权主体「本服务由兴业银行信用卡中心提供」 | — |

采集到的可变数据通过 `_collect_bill_info()` 返回并写进日志（如 `{'card': '标准白金信用卡(9636)', 'repayment_state': '已还清', 'amounts': [...], 'unbilled_date': '11月15日出账', 'env_version': 'sit v4.63.1'}`），排查问题时能看到当时的真实账务状态，但不影响用例结果。

对应断言手段：文本用 `assert_text_present`（任意标签）、图片/组件用 `assert_css_present`（如 `.amount` 金额块）、动态文本用 `assert_body_text_matches`（正则）、数量用 `assert_text_count_at_least`。

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

## 6. 常用 API

### 6.1 断言层 `common/assert_utils.py::AssertUtils`

| 方法 | 说明 | 返回 |
|---|---|---|
| `assert_true(condition, msg="")` | 布尔断言 | `condition` |
| `assert_equal(actual, expected, msg="")` | 相等断言 | `actual` |
| `assert_element_present(driver, locator, timeout=10, msg="")` | 元素存在断言 | `WebElement` |
| `assert_span_text_present(driver, text, ...)` | H5 span 文本断言 | `WebElement` |
| `assert_a_text_present(driver, text, ...)` | H5 a 标签文本断言 | `WebElement` |
| `assert_native_text_present(driver, text, ...)` | 原生控件文本断言 | `WebElement` |
| `assert_page_loaded(driver, expect_url=None, ...)` | 页面真实加载断言（URL + 标题 + readyState） | `url` |
| `assert_page_title_contains(driver, keyword, ...)` | 标题包含关键字断言 | `title` |
| `assert_url_contains(driver, fragment, ...)` | URL 包含片段断言（如路由 `/billMain`） | `url` |
| `assert_text_present(driver, text, ...)` | 任意标签（p/span/div/i…）文本断言 | `WebElement` |
| `assert_css_present(driver, css, ...)` | CSS 选择器存在断言（无文字组件，如图片印章） | `True` |
| `assert_body_text_matches(driver, pattern, ...)` | 正文正则匹配断言（金额/日期/版本号等动态文本） | 匹配到的字符串 |
| `assert_text_count_at_least(driver, text, at_least, ...)` | 元素数量下限断言（如「查账」应有 2 个） | 实际数量 |

### 6.2 业务层 `utils/weichat_utils.py`

#### 会话与启动

| 方法 | 说明 |
|---|---|
| `launch_weichat(timeout=30, restart=False, unlock=True)` | 唤醒 → 启动 → 等待主界面就绪（自动开 TalkBack） |
| `force_stop_weichat()` | 结束微信进程 |
| `get_current_activity()` | 取前台 Activity（如 `com.tencent.mm/.ui.LauncherUI`） |
| `wait_weichat_home()` / `is_weichat_home()` / `is_weichat_login_page()` | 首页/登录页判定（依赖控件树，需 TalkBack 开启） |
| `is_weichat_launcher()` | 用 activity 判断是否在主界面（`LauncherUI`），关掉 TalkBack 后仍可用 |

#### 入口与页面

| 方法 | 说明 |
|---|---|
| `open_fav_in_wechat(title, expect_url=None)` | **推荐入口**：我 → 收藏 → 点标题 → 切 WEBVIEW → 校验页面已加载 |
| `open_url_in_wechat(url)` | 【已停用】文件传输助手发链接再点击（受外链风控限制） |
| `wait_webview_loaded(expect_url=None)` | 等待并校验页面真正加载（排除错误页/拦截页），失败抛异常 |
| `ensure_xweb_debug()` | 确保 XWeb 调试开关已开启 |
| `wait_and_switch_webview(timeout=30)` | 等待并切到微信 webview 上下文 |
| `enter_chat_by_search(keyword)` / `enter_file_transfer_chat()` | 通过搜索进入指定会话 |
| `send_url_in_current_chat(url)` | 在当前会话发送文本/链接 |

#### 还原与工具

| 方法 | 说明 |
|---|---|
| `cleanup_after_test(...)` | 现场还原：回首页 + 关 TalkBack + 可选结束微信/回桌面；回首页失败自动冷启动兜底 |
| `back_to_weichat_home(max_back=8)` | 逐级返回微信主界面：activity 判定 + 卡住时清任务栈/冷启动 |
| `is_weichat_launcher()` | 用 activity 判断是否在微信主界面（`LauncherUI`），不依赖控件树，单次约 0.3s |
| `launch_weichat_launcher_by_clear_top()` | `am start --activity-clear-top` 一次性清掉 WebView/收藏/聊天子页 |
| `enable_talkback()` / `disable_talkback()` | 读屏服务开关 |
| `wait_for_element(locator, timeout)` | 显式等待元素（返回 None 而非抛异常；断言场景用 `AssertUtils`） |
| `check_zhangdan_exit()` | 轻量检查：断言账单页出现「账单」元素 |
| `check_bill_page(expect_url="/billMain")` | **账单页全要素检查**：路由/标题/卡片/本期账单/未出账单/查账入口/按钮/历史账单/现金分期/页脚，只断言稳定元素；返回采集到的业务数据 dict |
| `_collect_bill_info()` | 采集可变业务数据（还款状态、金额、出账日、版本号），仅供日志留痕 |

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
10. **页面报 `ERR_CONNECTION_REFUSED(-6)`**：域名解析正常但 TCP 被拒，通常是**服务端 IP 白名单未放通**当前手机出口 IP（不是微信拦截、不是脚本问题）。此前该场景下用例会因元素定位异常/无断言而"假通过"，现已由 `wait_webview_loaded()` 拦截并报错。
11. **网关 502 页的 `readyState` 同样是 `complete`**：SIT 总链的「1、账单查询」曾指向 `/cos/security/direct/html/webapp/v3/query/index.html`（该路径 502，同页 `/html/webapp/...` 正常），标题为「网关错误」。只判断 `readyState` 会假通过，`assert_page_loaded()` 现已按标题关键字（`网关错误`/`502`/`504`/`Bad Gateway` 等）拦截，并在日志里打出命中的关键字。

---

## 8. 版本与更新日志

> 维护约定：每次改动代码/文档后，①刷新文首"最后更新时间 + 当前版本"；②在本节追加一条记录（版本 / 日期 / 变更摘要）。

| 版本 | 日期 | 变更摘要 |
|---|---|---|
| v1.4.0 | 2026-11-03 | 现场还原重构 + 错误页识别：新增 `is_weichat_launcher()`（activity 判定主界面，单次 ~0.3s，关 TalkBack 后仍可用）；`back_to_weichat_home()` 改用 activity 判定、`max_back` 6→8、连续两次无进展时 `am start --activity-clear-top` 清任务栈、仍失败冷启动；`cleanup_after_test()` 回首页失败自动冷启动兜底；`AssertUtils` 新增 `match_error_title()`，`assert_page_loaded()` 改为按标题关键字包含匹配（补 `网关错误`/`502`/`503`/`504`/`Bad Gateway` 等），修掉"网关 502 页 `readyState=complete` 假通过"；`wait_webview_loaded()` 去掉重复的错误页名单，统一走 `DEFAULT_ERROR_TITLES`。**验证情况**：两次实机跑均因 SIT 总链链接指向 `/cos/security/direct/...`（网关 502）在账单页失败，非代码问题；还原链路在"卡住"分支验证通过（2 次 `back` 无进展 → 清任务栈 → `LauncherUI`，回首页=True）；错误页识别已用假 driver 离线验证 |
| v1.3.0 | 2026-11-03 | 账单页全要素检查：新增 `check_bill_page()`（路由/标题/卡片信息/本期账单/未出账单/查账入口数量/还款按钮/历史账单/现金分期/页脚共 19 项断言）与 `_collect_bill_info()`（采集可变数据只记日志）；断言层新增 `assert_text_present` / `assert_css_present` / `assert_body_text_matches` / `assert_text_count_at_least` / `assert_url_contains`；明确"还款状态、金额、出账日、营销文案、版本号"等会变化的元素**不进断言**；新增第 10 节「扩展开发指南」（自己写脚本的规范、模板与定位速查）。实测 `1 passed in 111.72s` |
| v1.2.0 | 2026-11-03 | 断言分层：新增 `common/assert_utils.py::AssertUtils`（元素/页面/布尔/相等断言，失败抛 `AssertionError` 并带业务语义信息）；`WeichatUtils` 的 `click_link_sit/click_link_weixin/click_link_title/check_zhangdan_exit/wait_webview_loaded` 及会话/收藏入口的元素校验改为内部断言并返回结果；`test_code_demo.py` 不再写 assert。实测 `1 passed in 108.76s`，每步日志可见"断言通过｜…" |
| v1.1.0 | 2026-11-03 | 新增 `wait_webview_loaded()` 页面加载校验（URL/标题/readyState 三重判断），收藏入口自动调用；`check_zhangdan_exit()` 返回布尔值，用例改为显式 `assert`，杜绝错误页假通过；白名单放通后实机验证：`1 passed in 108.06s` |
| v1.0.0 | 2026-11-01 | 首个完整文档版本：`open_fav_in_wechat` 收藏入口、`ensure_xweb_debug` 调试自开、`cleanup_after_test` 现场还原、全项目 print→logger、`.gitignore` 修正 |
| v0.9.0 | 2026-11-01 | 打通端到端链路：TalkBack 放开无障碍、会话进入与发链接、WEBVIEW 上下文修正（主进程 `com.tencent.mm`）、XWeb 调试自动开启 |
| v0.1.0 | 2025-04-20 | 项目骨架：Appium 会话工厂、命令执行封装、元素定位工具、日志与基础用例结构 |

---

## 9. 待办 / 后续规划

- [x] 服务端 IP 白名单已放通，首页加载成功断言已补齐（`wait_webview_loaded`）；
- [ ] 封装「扫一扫」入口，支持任意 URL 参数化打开；
- [ ] 引入 `reports/` HTML 报告与失败自动截图；
- [ ] 清理 `weichat_utils.py` 中已被 `wait_and_switch_webview()` 取代的旧方法（`switch_content` / `wait_for_content` / `click_test_link` 等）。

---

## 10. 扩展开发指南（自己写脚本）

### 10.1 三条铁律

1. **测试函数只编排流程**，不写 `assert`、不写 `find_element`；
2. **断言只在 `common/assert_utils.py`**，失败信息写清"哪个页面、缺什么、可能原因"；
3. **一个业务动作 = 一个业务方法**："断言元素存在 → 动作 → 返回结果"，放在 `utils/weichat_utils.py`。

> 为什么这么分：断言集中后，元素选择器/文案变了只改一处；失败信息直接指向步骤，而不是所有用例都报同一个 `AssertionError`。

### 10.2 新增一个页面（以"还款页"为例）

**第 1 步：先探页面，拿到真实文案与结构**

```bash
# 手动走到目标页后，抓 DOM / 文案 / 是否 vConsole 遮挡
adb exec-out screencap -p > /tmp/page.png
```

在 Appium 会话里跑一段临时代码落盘 `driver.page_source`，比对着截图确认：区块标题、字段标签、按钮文案、金额的 class（判断哪个能用 CSS 稳定选中）、哪些文字是动态数据。

**第 2 步：需要新断言手段时，才去加断言方法**

已有手段基本够用（文本/链接/原生控件/CSS/正则/数量/页面加载），只有遇到"新形态"才扩展 `AssertUtils`，例如"元素可点击""元素数量等于 N""输入框可输入"：

```python
def assert_element_enabled(self, driver, locator, timeout=10, msg=""):
    element = self.assert_element_present(driver, locator, timeout, msg)
    assert element.is_enabled(), msg or f"元素不可用：{locator[1]}"
    logger.info("断言通过｜元素可交互")
    return element
```

**第 3 步：在 `WeichatUtils` 加业务方法**

```python
def open_repay_page(self, expect_url="/repayMain"):
    """
    description: 从账单页进入还款页并校验页面已加载
    :return: True
    """
    entry = self.assert_util.assert_text_present(
        self.driver, "还款", msg="账单页未出现「还款」按钮，可能页面未加载完成")
    entry.click()
    time.sleep(2)
    self.assert_util.assert_page_loaded(self.driver, expect_url=expect_url, timeout=15,
                                        msg="还款页未加载出来")
    self.assert_util.assert_page_title_contains(self.driver, "还款")
    return True

def check_repay_page(self):
    """还款页结构检查：只断言固定标签与入口，金额/优惠等可变内容只采集"""
    au = self.assert_util
    au.assert_text_present(self.driver, "还款金额", msg="还款页缺少「还款金额」字段")
    au.assert_text_present(self.driver, "立即还款", msg="还款页未出现「立即还款」按钮")
    return True
```

**第 4 步：写在用例里（只编排）**

```python
def test_repay_01(self):
    self.weichat_util.launch_weichat()
    self.weichat_util.open_fav_in_wechat(FAV_TITLE, expect_url=EXPECT_URL)
    self.weichat_util.click_link_sit()
    self.weichat_util.click_link_weixin()
    self.weichat_util.click_link_title('2、还款')
    self.weichat_util.check_repay_page()
```

### 10.3 用例文件模板（复制即用）

```python
# -*- coding: utf-8 -*-
from common.base_test import BaseTest
from common.logger import get_logger
from utils.weichat_utils import WeichatUtils

logger = get_logger()

FAV_TITLE = "测试环境首页"
EXPECT_URL = "uatxyk.cibfintech.com"


class TestXxx(BaseTest):

    def setup_method(self, method):
        super().setup_method(method)
        self.weichat_util = WeichatUtils()

    def test_xxx_01(self):
        self.weichat_util.launch_weichat()
        self.weichat_util.open_fav_in_wechat(FAV_TITLE, expect_url=EXPECT_URL)
        # ...业务步骤（每个方法内部自带断言）

    def teardown_method(self):
        super().teardown()
        # 默认：回微信首页 + 关 TalkBack；用例改过数据时用 stop_weichat=True 彻底隔离
        self.weichat_util.cleanup_after_test(stop_weichat=False, close_talkback=True)
        self.weichat_util.driver.quit()
```

### 10.4 断言什么、不断言什么

- **断言**：页面路由/标题、区块标题、字段标签、按钮与入口、固定的版权文案、稳定的数量关系（如「查账」2 个）；
- **不要断言**：金额数值、还款状态（已还清/逾期）、出账日期、优惠/角标文案、版本号、环境标识 —— 这些每次跑都可能不同，断言只会制造假失败；用 `_collect_bill_info()` 这类方法**采集并写日志**即可。

判断标准一句话：**这条断言在"业务正常"的前提下，明天、下个月、换个账号跑，结果是否一定一样？** 不一定，就别写进断言。

### 10.5 定位速查

| 场景 | 写法 |
|---|---|
| H5 文本（span/a） | `assert_span_text_present` / `assert_a_text_present` |
| H5 文本（标签不确定） | `assert_text_present`（任意标签） |
| H5 无文字组件（图片印章、图标） | `assert_css_present(driver, ".paid-off")` |
| 动态文本（金额/日期/版本） | `assert_body_text_matches(driver, r"¥\d+\.\d+")` |
| 数量关系 | `assert_text_count_at_least(driver, "查账", 2)` |
| 原生控件（微信界面） | `assert_native_text_present` / `wait_for_element` + `AppiumBy` |

### 10.6 运行与提交

```bash
# 单条用例
env -u http_proxy -u https_proxy PYTHONPATH=$PWD \
  /Library/Frameworks/Python.framework/Versions/3.10/bin/python3 -m pytest \
  scripts/redmi_note_11pro/test_xxx.py -s -v
```

提交前顺手做三件事：①刷新文首"最后更新时间/当前版本"；②在第 8 节加一条更新日志；③确认 `logs/` 下没有把运行日志提交上去。
