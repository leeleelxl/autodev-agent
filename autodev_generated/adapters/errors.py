from pydantic import BaseModel   # 修复：缺失导入
from typing import Any

class ErrorSchema(BaseModel):
    code: str
    message: str
    detail: Any | None = None
    trace_id: str | None = None