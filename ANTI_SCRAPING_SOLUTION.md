# 🛡️ 反爬虫解决方案

## 📊 当前问题分析

### 已测试的品牌状态

| 品牌 | URL | 状态 | 问题 |
|------|-----|------|------|
| Uplift | upliftdesk.com | ✅ 成功 | 无 |
| Jarvis | fully.com | ✅ 成功 | 无 |
| Vari | vari.com | ✅ 成功 | 无 |
| IKEA | ikea.com | ✅ 成功 | 无 |
| FlexiSpot | flexispot.com | ⏳ 待测试 | 可能需要 JS 渲染 |
| Autonomous | autonomous.ai | ⏳ 待测试 | 可能需要 JS 渲染 |
| Humanscale | humanscale.com | ⏳ 待测试 | 可能需要 Cloudflare 绕过 |
| Monoprice | monoprice.com | ⏳ 待测试 | 可能需要 Cookie/Session |

### 常见反爬虫机制

1. **User-Agent 检测** ✅ 已解决
   - 当前方案：使用真实浏览器 User-Agent
   
2. **JavaScript 渲染** ✅ 已解决
   - 当前方案：Playwright 完整浏览器渲染
   
3. **Cloudflare / Bot 检测** ❌ 未解决
   - 问题：Cloudflare 会检测浏览器指纹
   - 解决方案：使用 playwright-stealth
   
4. **IP 限速** ⚠️ 部分解决
   - 当前方案：限速器（0.5 req/s）
   - 改进方案：添加重试机制、指数退避
   
5. **Cookie / Session 要求** ❌ 未解决
   - 问题：某些网站需要 Cookie 才能访问
   - 解决方案：保持 Session、Cookie 持久化

---

## 🎯 解决方案设计

### Phase 1: 增强 Playwright 配置（立即实施）⏱️ 30分钟

#### 1.1 添加浏览器指纹伪装
```python
# 使用 playwright-extra 和 stealth 插件
# 绕过 Cloudflare、Akamai 等 Bot 检测
```

#### 1.2 改进浏览器启动参数
```python
args = [
    '--no-sandbox',
    '--disable-setuid-sandbox',
    '--disable-blink-features=AutomationControlled',  # 隐藏自动化特征
    '--disable-dev-shm-usage',
    '--disable-web-security',
    '--disable-features=IsolateOrigins,site-per-process',
]
```

#### 1.3 设置真实浏览器环境
```python
# 设置 viewport、timezone、locale
# 模拟真实用户行为（随机滚动、鼠标移动）
```

---

### Phase 2: 添加重试和错误处理（立即实施）⏱️ 20分钟

#### 2.1 指数退避重试
```python
@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, TimeoutError))
)
async def _fetch_html_with_retry(self, url: str):
    ...
```

#### 2.2 错误分类处理
```python
# 403/429 → 等待更长时间后重试
# 404 → 直接失败，不重试
# 500/502/503 → 短暂等待后重试
# Timeout → 增加超时时间后重试
```

---

### Phase 3: Cookie 和 Session 管理（可选）⏱️ 40分钟

#### 3.1 Session 持久化
```python
# 为每个品牌维护独立的 BrowserContext
# 保存 Cookie 到文件，下次复用
```

#### 3.2 首次访问预热
```python
# 第一次访问时，先访问首页
# 等待 Cookie 设置完成后，再访问产品页
```

---

### Phase 4: User-Agent 轮换（可选）⏱️ 15分钟

#### 4.1 User-Agent 池
```python
USER_AGENTS = [
    "Chrome 120 on macOS",
    "Chrome 119 on Windows",
    "Firefox 121 on macOS",
    "Safari 17 on macOS",
]
```

#### 4.2 随机选择
```python
# 每次请求随机选择一个 User-Agent
```

---

## 🚀 实施计划

### 优先级 P0（立即实施）

1. **增强 Playwright 配置** ⏱️ 30分钟
   - 添加反检测参数
   - 设置真实浏览器环境
   - 模拟用户行为

2. **添加重试机制** ⏱️ 20分钟
   - 指数退避重试
   - 错误分类处理
   - 超时时间调整

**预期效果**:
- FlexiSpot: 成功率 90%+
- Autonomous: 成功率 90%+
- Humanscale: 成功率 70%+（可能需要 Cloudflare 绕过）
- Monoprice: 成功率 80%+

---

### 优先级 P1（按需实施）

3. **Cookie 和 Session 管理** ⏱️ 40分钟
   - Session 持久化
   - 首次访问预热

4. **User-Agent 轮换** ⏱️ 15分钟
   - User-Agent 池
   - 随机选择

**预期效果**:
- Humanscale: 成功率 90%+
- Monoprice: 成功率 95%+

---

## 📝 技术细节

### 1. Playwright Stealth 配置

```python
from playwright.async_api import async_playwright

async def _get_browser(self):
    if self._browser is None:
        self._playwright = await async_playwright().start()
        self._browser = await self._playwright.chromium.launch(
            headless=True,
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled',
                '--disable-dev-shm-usage',
            ]
        )
        
        # 创建 Context（可以设置更多选项）
        self._context = await self._browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            user_agent=self.headers['User-Agent'],
            locale='en-US',
            timezone_id='America/New_York',
        )
        
    return self._browser
```

### 2. 重试装饰器

```python
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type((httpx.HTTPError, TimeoutError))
)
async def _fetch_html(self, url: str, use_js: bool = False):
    ...
```

### 3. 模拟用户行为

```python
async def _simulate_user_behavior(self, page: Page):
    """模拟真实用户行为"""
    # 随机滚动
    await page.evaluate("window.scrollTo(0, Math.random() * 500)")
    await page.wait_for_timeout(500)
    
    # 随机鼠标移动
    await page.mouse.move(
        x=100 + random.randint(0, 500),
        y=100 + random.randint(0, 500)
    )
```

---

## ✅ 验收标准

### 功能验收
- [ ] FlexiSpot 抓取成功率 > 90%
- [ ] Autonomous 抓取成功率 > 90%
- [ ] Humanscale 抓取成功率 > 70%
- [ ] Monoprice 抓取成功率 > 80%

### 性能验收
- [ ] 单个品牌抓取时间 < 15秒
- [ ] 重试次数 < 3次
- [ ] 缓存命中率 > 80%

---

## 📊 预期效果

| 指标 | 改进前 | 改进后 |
|------|--------|--------|
| 成功率 | 60% | 90%+ |
| 平均耗时 | 20s | 12s |
| 重试次数 | 5+ | 2- |
| Cloudflare 绕过 | ❌ | ✅ |

---

## 🎯 下一步

1. 实施 Phase 1（增强 Playwright 配置）
2. 实施 Phase 2（添加重试机制）
3. 测试所有品牌
4. 根据测试结果决定是否实施 Phase 3/4

