from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from loguru import logger

# Импортируем из единого места определений
from src.exceptions.exceptions import NotFoundError


def register_exception_handlers(app: FastAPI):
    @app.exception_handler(NotFoundError)
    async def not_found_handler(request: Request, exc: NotFoundError):
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={
                "detail": f"{exc.entity} with identifier '{exc.identifier}' not found"
            },
        )

    @app.exception_handler(Exception)
    async def unexpected_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {exc}", exc_info=True)
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {},
                }
            },
        )
