from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from ..schemas import RunResult, SpiderConfigIn, TestResult
from ..services.config_spider import (
    get_latest_results_csv,
    run_config_spider_full,
    test_config_spider,
)


router = APIRouter(tags=["config-spider"])


@router.get("/health")
async def health_check() -> dict:
    """
    简单健康检查接口，便于确认后端服务和路由前缀工作正常。
    """
    return {"status": "ok"}


@router.post("/config-spider/test", response_model=TestResult)
async def test_config(config: SpiderConfigIn) -> TestResult:
    """
    测试一条/一页抓取，用于前端校验选择器是否正确。
    """
    try:
        return await test_config_spider(config)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/config-spider/run", response_model=RunResult)
async def run_config(config: SpiderConfigIn) -> RunResult:
    """
    正式运行配置爬虫，当前版本采用同步方式。
    """
    try:
        return await run_config_spider_full(config)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except Exception as exc:  # pragma: no cover - 防御性兜底
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@router.get(
    "/config-spider/export/csv",
    response_class=Response,
)
async def export_csv() -> Response:
    """
    导出最近一次运行结果为 CSV。
    """
    csv_text = get_latest_results_csv() or ""
    # UTF-8 BOM for better Excel compatibility on Windows.
    csv_bytes = b"\xef\xbb\xbf" + csv_text.encode("utf-8")
    return Response(
        content=csv_bytes,
        media_type="text/csv; charset=utf-8",
        headers={"Content-Disposition": 'attachment; filename="results.csv"'},
    )


