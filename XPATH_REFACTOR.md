## XPath 解析逻辑重构对比（Scrapy/Parsel 风格）

本文档描述配置化爬虫（`config_spider_runtime`）中与 XPath/CSS 选择器相关的重构点，目标是在不改变既有功能的前提下，让 XPath 的填写与解析更贴近 Scrapy 的 Selector 使用习惯（链式调用、相对 XPath、表达式可读性更好）。

### 影响范围

- `bald_spider.http.response.Response`：补齐 Scrapy 常用的 `css()` 接口，并统一缓存 Selector 实例。
- `config_spider_runtime.factory`：重构“列表节点/字段/详情链接”的选择器执行逻辑，加入相对 XPath 规范与回退兼容策略。

---

## 重构前（问题点）

### 1) Selector API 不完整

- `Response` 仅提供 `xpath()`，配置里虽然允许 `selector_type=css`，但实际仍会走 `xpath()`（CSS 分支是占位逻辑）。

### 2) 节点上下文中容易误用 `//`

- 在“列表节点循环”中，字段选择器通过 `node.xpath(fc.selector)` 执行。
- 如果填写的是 `//a/@href` 这类表达式，XPath 会从整棵文档树重新开始匹配，导致：
  - 抽取结果不稳定（可能拿到页面中第一条匹配，而不是当前节点下的匹配）
  - 表达式被迫写得很“长很绕”（为了避免误匹配，必须把路径写到很深）

---

## 重构后（优化点）

### 1) Scrapy 风格的链式 Selector 使用方式

- `Response` 新增：
  - `selector` 属性：缓存并复用 `parsel.Selector(self.text)`
  - `css()` 方法：与 `xpath()` 并列，便于 Scrapy 风格链式调用
- 现在可以在任意解析逻辑中使用：
  - `response.css("a::attr(href)").get()`
  - `response.xpath("//div").xpath(".//a/@href").get()`

### 2) 节点上下文优先使用相对 XPath（并带回退）

在列表页解析时，对字段与详情链接选择器做了“Scrapy 习惯化”处理：

- 若在节点上下文中填写了以 `/` 或 `//` 开头的 XPath，则先自动转换为相对 XPath（前置 `.`）：
  - `//a/@href` → `.//a/@href`
  - `/a/@href` → `./a/@href`
- 为兼容旧配置：若相对 XPath 无结果，会回退执行原表达式（保持历史行为不被破坏）。

### 3) 选择器执行逻辑统一

- 新增统一入口 `_select(...)`：
  - CSS：优先执行 `.css()`；若“误填了 XPath”（以 `/` 或 `//` 开头）且 CSS 无结果，会回退执行 `.xpath()`（兼容旧用法）。
  - XPath：按“整页/节点上下文”选择是否启用相对 XPath 策略。

### 4) 页面级抽取与翻页配置

- 字段新增 `scope` 概念：
  - `scope=node`：字段 XPath/CSS 在“列表节点上下文”执行（推荐使用 `.//...`）
  - `scope=page`：字段 XPath/CSS 在“整页 response 上下文”执行（适合标题、面包屑、页面固定信息）
- 新增 `next_page_selector`：
  - 填写“下一页 URL”的 XPath/CSS 后，解析时会自动 `yield Request(next_url, callback=parse)` 继续抓取下一页

---

## 行为保持与兼容性说明

- 原有 `xpath()` 行为不变：仍返回 `parsel.SelectorList`，可继续使用 `.get()`/`.getall()`。
- 配置化爬虫的字段抽取逻辑保持不变：
  - 仍然按 `from_page=list/detail` 分别抽取
  - 仍然按 `attr=text/href/src/自定义属性` 进行取值与 `urljoin`
- 为避免破坏历史配置：
  - 节点上下文相对 XPath：先相对、后回退
  - CSS 选择器：先 CSS、必要时回退 XPath

---

## 可读性与维护性改进建议（填写 XPath 的推荐写法）

在“列表节点循环”场景（`for node in response.xpath(list_selector)`）中，建议使用：

- 取节点下文本：`.//h2/text()`
- 取节点下链接：`.//a/@href`
- 取节点自身某属性：`./@data-id`

避免在节点上下文里写长链条的绝对路径（例如从根开始的 `//div[@id="..."]/.../a/@href`），让表达式更短、更清晰。

---

## 性能影响（定性说明）

- 节点上下文误用 `//` 时，容易触发从文档根重新搜索，匹配范围更大；重构后会优先变为相对 XPath，通常能减少搜索空间。
- 对于原本就正确使用 `.//` 的表达式，重构不会引入额外开销（相对表达式与原表达式一致，不触发回退）。

