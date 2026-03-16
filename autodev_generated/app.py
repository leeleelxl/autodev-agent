from fastapi import FastAPI
from adapters.routers import router
from adapters.middleware import global_exception_handler
from adapters.database import init_db
from contextlib import asynccontextmanager
import uvicorn

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(
    title="CleanAuth",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.include_router(router)
app.add_exception_handler(Exception, global_exception_handler)

if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)