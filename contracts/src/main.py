from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware

from src.middleware.request_id import RequestIDMiddleware
from src.middleware.logging import LoggingMiddleware
from src.db.pools import init_pools, close_pools
from src.routers.organisations import router as organisations_router
from src.routers.tariffs import router as tariffs_router
from src.routers.communications import router as communications_router
from src.routers.payments import router as payments_router
from src.routers.services import router as services_router
from src.logger_config import setup_logger
from src.core.handlers import register_exception_handlers

logger = setup_logger()
logger.info("✅ Contracts service logger configured")


@asynccontextmanager
async def lifespan(app):
    logger.info("🚀 Initializing database connection pools...")
    await init_pools()
    yield
    logger.info("🛑 Closing database connection pools...")
    await close_pools()


app = FastAPI(lifespan=lifespan, title="Contracts Service", version="0.1.0")

register_exception_handlers(app)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Подключение роутеров
app.include_router(
    organisations_router, prefix="/organisations", tags=["Organisations"]
)
app.include_router(services_router, prefix="/services", tags=["Services"])
app.include_router(tariffs_router, prefix="/tariffs", tags=["Tariffs"])
app.include_router(
    communications_router, prefix="/communications", tags=["Communications"]
)
app.include_router(payments_router, prefix="/payments", tags=["Payments"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("src.main:app", host="0.0.0.0", port=8004, reload=True)
