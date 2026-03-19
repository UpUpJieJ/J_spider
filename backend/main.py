from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers import config_spider


def create_app() -> FastAPI:
    app = FastAPI(title="bald_spider Config API")

    # CORS：默认允许本地前端开发地址，后续可根据需要调整
    origins = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 路由前缀统一为 /api
    app.include_router(config_spider.router, prefix="/api")

    return app


app = create_app()

