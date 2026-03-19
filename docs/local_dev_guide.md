# bald_spider 本地开发指南

这份文档面向当前仓库的日常开发与联调，默认你已经使用 `uv` 创建好了虚拟环境，并且 Python 依赖已经可用。

## 1. 项目包含什么

当前仓库主要有两部分：

- `bald_spider/`：异步爬虫框架本体
- `backend/` + `frontend/`：配置式爬虫 GUI

常见开发场景通常分为 3 类：

1. 只运行框架示例爬虫
2. 只启动 FastAPI 后端
3. 启动前后端联调配置式爬虫页面

---

## 2. 进入项目

PowerShell 示例：

```powershell
cd e:\猿人学\J_spider
```

如果你已经激活虚拟环境，后面的 `python ...` 命令可以直接运行。

如果你平时更习惯不手动激活虚拟环境，也可以把文中的 `python ...` 替换成：

```powershell
uv run python ...
```

---

## 3. 运行框架示例爬虫

你已经验证过这条命令可以工作，后续本地调试建议继续用模块方式运行：

```powershell
python -m tests.baidu_spider.run
```

这样运行的好处是：

- Python 会自动把仓库根目录加入模块搜索路径
- 不容易再遇到 `ModuleNotFoundError: bald_spider`
- 更适合后续扩展测试或脚本入口

如果只是验证框架主链路，这条命令通常就是最直接的 smoke test。

---

## 4. 启动后端 FastAPI

后端入口文件：

- `backend/main.py`

启动命令：

```powershell
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

启动成功后，可访问：

- 健康检查：`http://127.0.0.1:8000/api/health`
- OpenAPI 文档：`http://127.0.0.1:8000/docs`

当前主要接口：

- `POST /api/config-spider/test`
- `POST /api/config-spider/run`
- `GET /api/config-spider/export/csv`

---

## 5. 启动前端 Vite

前端目录：

- `frontend/`

首次启动前，如果还没安装 Node 依赖：

```powershell
cd frontend
npm install
```

开发模式启动：

```powershell
cd frontend
npm run dev
```

默认访问地址通常是：

- `http://localhost:5173`

前端默认会请求：

- `http://localhost:8000/api`

对应实现位于：

- `frontend/src/features/configSpider/api.ts`

---

## 6. 前后端联调方式

推荐同时开两个终端窗口。

终端 1：启动后端

```powershell
cd e:\猿人学\J_spider
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

终端 2：启动前端

```powershell
cd e:\猿人学\J_spider\frontend
npm run dev
```

然后在浏览器打开：

```text
http://localhost:5173
```

联调流程建议按下面顺序走：

1. 先访问 `http://127.0.0.1:8000/api/health`，确认后端已启动
2. 再打开前端页面
3. 填写 `start_urls`、列表选择器、字段选择器
4. 先点测试，再点正式运行
5. 结果正常后再导出 CSV

---

## 7. 前端改后端地址

如果前端不想连默认的 `http://localhost:8000/api`，可以在 `frontend/` 目录新增 `.env` 文件：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

修改后需要重启前端开发服务器。

---

## 8. 常用命令速查

在仓库根目录：

```powershell
python -m tests.baidu_spider.run
python -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8000
```

在前端目录：

```powershell
npm install
npm run dev
npm run build
```

---

## 9. 常见问题

### 9.1 `ModuleNotFoundError: bald_spider`

优先用模块方式运行：

```powershell
python -m tests.baidu_spider.run
```

不要直接在子目录里执行：

```powershell
python run.py
```

### 9.2 前端页面打开了，但请求失败

优先检查：

1. 后端是否已启动在 `127.0.0.1:8000`
2. `frontend/.env` 是否把地址写错
3. 浏览器控制台或后端终端里是否有 400/500 报错

### 9.3 导出 CSV 没内容

当前导出的是“最近一次运行结果”的内存数据。也就是说：

- 后端进程重启后，之前结果会丢失
- 必须先成功运行一次 `run`，再导出 CSV

---

## 10. 推荐开发顺序

如果你准备继续开发这个仓库，建议日常流程是：

1. 改框架内核时，先跑 `python -m tests.baidu_spider.run`
2. 改配置爬虫后端时，启动 FastAPI，先测 `/api/health`
3. 改配置爬虫前端时，打开 Vite 页面做联调
4. 改选择器提取逻辑时，优先补 `tests/config_spider_*` 这一类冒烟测试

这样成本最低，也最容易快速定位问题是在框架、后端还是前端。
