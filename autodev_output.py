
import uuid
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from src.config import settings
from src.infrastructure.sqlite.database import create_db_and_tables
from src.presentation.routes import auth_router
from src.presentation.error_handler import global_exception_handler
from src.presentation.middlewares.trace_id import TraceIdMiddleware


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """应用生命周期：启动时建表"""
    create_db_and_tables()
    yield


app = FastAPI(
    title="Clean Auth Service",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# CORS 可根据需要调整
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# TraceId
app.add_middleware(TraceIdMiddleware)

# 全局异常处理
app.add_exception_handler(Exception, global_exception_handler)

# 路由
app.include_router(auth_router, prefix="/auth", tags=["Authentication"])


@app.get("/health", summary="健康检查")
async def health() -> dict:
    return {"status": "ok"}