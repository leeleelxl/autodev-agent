from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from adapters.errors import ErrorSchema
import uuid
import traceback

async def global_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    trace_id = str(uuid.uuid4())
    if isinstance(exc, RequestValidationError):
        return JSONResponse(
            status_code=422,
            content=ErrorSchema(
                code="VALIDATION_ERROR",
                message="Request validation failed",
                detail=exc.errors(),
                trace_id=trace_id,
            ).model_dump(),
        )
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=400,
            content=ErrorSchema(
                code="BUSINESS_ERROR",
                message=str(exc),
                trace_id=trace_id,
            ).model_dump(),
        )
    traceback.print_exc()
    return JSONResponse(
        status_code=500,
        content=ErrorSchema(
            code="INTERNAL_ERROR",
            message="Internal server error",
            trace_id=trace_id,
        ).model_dump(),
    )