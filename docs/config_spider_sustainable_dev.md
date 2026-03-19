# Config Spider 可持续开发文档

## 1. 本次优化目标与结果

本次改造聚焦 4 个已识别问题，并完成落地修复：

1. `max_items` 未实际生效  
已在动态 Spider 中增加统一限流逻辑，达到上限后停止继续产出并尝试提前结束运行。

2. 前端会提交空 URL / 空字段  
新增前端配置规范化与校验层，提交前会 trim + 过滤空项；后端也增加二次清洗。

3. `attr=text` 取值不符合直觉  
由 `node.get()` 改为节点纯文本提取（`string(.)`），避免拿到整段 HTML。

4. UI 文案与真实配置键不一致  
文案从 `CONCURRENT_REQUESTS` 修正为框架实际使用的 `CONCURRENCY`。

---

## 2. 当前推荐结构

### 2.1 前端（Feature-First）

```text
frontend/src/
  App.tsx
  features/
    configSpider/
      index.ts
      ConfigSpiderPage.tsx
      api.ts
      types.ts
      constants.ts
      normalize.ts
      validation.ts
      hooks/
        useConfigSpiderRunner.ts
      components/
        ConfigPanel.tsx
        ResultPanel.tsx
  api/configSpider.ts          # 兼容层，转发到 feature api
  types/configSpider.ts        # 兼容层，转发到 feature types
```

设计原则：

- 业务聚合：同一业务（config spider）下，页面、组件、类型、API、校验、规范化放在同目录。
- 兼容迁移：`src/api` 与 `src/types` 保留转发层，避免一次性改动过大。
- 单向数据流：`ConfigSpiderPage` 持有状态，组件只负责展示与事件回调。

### 2.2 后端与内核

- `backend/services/config_spider/service.py`  
负责编排 test/run/export 用例，调用 runtime 并返回结果。

- `backend/services/config_spider/mapper.py`  
负责 DTO 清洗与 `SpiderConfig` 构建（URL/字段/可选文本统一标准化）。

- `backend/routers/config_spider.py`  
接口异常语义统一：配置错误统一返回 HTTP 400。

- `config_spider_runtime/factory.py`  
动态 Spider 的核心行为（字段提取、翻页、详情追踪、`max_items` 限制）。

---

## 3. 关键数据流（前后端）

1. 用户在 `ConfigPanel` 修改配置。
2. `ConfigSpiderPage` 执行 `validateBeforeTest/Run`。
3. 通过 `normalizeConfigForSubmit` 清洗 payload。
4. `useConfigSpiderRunner` 调用 `api.ts` 请求后端。
5. 后端 `mapper.py` 再次清洗并转 `SpiderConfig`，`service.py` 编排运行流程。
6. `ConfigSpiderFactory` 生成动态 Spider 并执行。
7. 结果进入 `InMemoryResultStore`，前端在 `ResultPanel` 展示，CSV 由后端导出。

---

## 4. 变更清单（代码落点）

- `config_spider_runtime/factory.py`
  - `text` 提取改为纯文本。
  - `href/src` 空值保护。
  - 增加 `max_items` 计数与停止逻辑。

- `backend/services/config_spider/mapper.py`
  - 新增 URL / 可选文本清洗函数。
  - 过滤无效字段（缺 name 或 selector）。
  - `start_urls` 在 test/run 中都基于清洗后的值校验。

- `backend/services/config_spider/service.py`
  - 统一编排 test/run/export 三条链路。
  - 与结果存储解耦，方便后续替换存储实现。

- `backend/routers/config_spider.py`
  - `test` 接口补充 `ValueError -> HTTP 400`。

- `frontend/src/features/configSpider/*`
  - 完成页面拆分、状态 hook 抽离、校验与规范化模块化。

---

## 5. 后续开发规范（建议）

1. 新增配置项时，按顺序更新：
   - `types.ts`
   - `constants.ts`
   - `normalize.ts`
   - `validation.ts`
   - `ConfigPanel.tsx`
   - 后端 `schemas.py` + `services/config_spider/mapper.py` + `services/config_spider/service.py`

2. 新增接口时，统一放在 `features/configSpider/api.ts`，组件中禁止直接 `fetch`。

3. 复杂状态优先放到 `hooks/`，组件仅接收 props，避免回到“大一统 App.tsx”。

4. 提取逻辑变更优先在 `factory.py` 做单点收敛，避免散落在 service/router。

5. 每次改动至少验证 3 条路径：
   - 无效输入是否被前端阻断。
   - 后端是否仍能兜底返回 400。
   - `test/run/export` 三条链路是否连通。

---

## 6. 已知边界

- 当前结果存储仍是内存态，进程重启会丢失。
- `max_items` 达到后会尽量提前停止，但并发场景可能仍有少量已在途请求。
- 尚未引入前端自动化测试（建议后续补 Vitest + React Testing Library）。

