# alpha_hook/src/routers/webhook.py
"""
Роутер для обработки вебхуков от Альфа-Банка
"""

from fastapi import APIRouter, Depends, Request
from loguru import logger
import json
import uuid

from src.dependencies.webhook import get_validated_payload
from src.services.db_service import save_webhook_result
from src.middleware.request_id import request_id_ctx
from src.db.pools import get_write_pool
from src.schemas.webhook import WebhookPayload

router = APIRouter(tags=["Alpha Bank SBP Webhooks"])


@router.post("/callback")
async def handle_webhook(
        request: Request,
        payload: WebhookPayload | None = Depends(get_validated_payload)
):
    """
    Обработка вебхука от Альфа-Банка.

    Flow:
    1. Логируем входящий запрос
    2. Получаем результат валидации из dependencies
    3. Сохраняем в БД через service
    4. Всегда возвращаем 200 OK
    """
    request_id = request_id_ctx.get()

    # 1️⃣ ЛОГИРОВАНИЕ: Входящий запрос
    body = await request.body()
    body_text = body.decode('utf-8', errors='ignore')
    content_type = request.headers.get("content-type", "")

    logger.info(
        "📥 INCOMING WEBHOOK",
        extra={
            "request_id": request_id,
            "content_type": content_type,
            "body_length": len(body_text),
            "body_preview": body_text[:200] + ("..." if len(body_text) > 200 else ""),
            "headers": dict(request.headers),
            "client_host": request.client.host if request.client else "unknown",
            "layer": "router"
        }
    )

    try:
        # Получаем пул для записи
        pool = get_write_pool()

        # Сохраняем через сервисный слой
        result = await save_webhook_result(
            pool=pool,
            raw_body=body_text,
            content_type=content_type,
            validated_payload=payload,
            request_id=request_id
        )

        # 2️⃣ ЛОГИРОВАНИЕ: Успешная обработка
        logger.info(
            "✅ WEBHOOK PROCESSED SUCCESSFULLY",
            extra={
                "request_id": request_id,
                "db_result": result,
                "layer": "router"
            }
        )

    except Exception as e:
        # 3️⃣ ЛОГИРОВАНИЕ: Критическая ошибка (не должно происходить)
        logger.exception(
            "🔥 CRITICAL ERROR IN WEBHOOK HANDLER",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "layer": "router"
            }
        )

    # Всегда возвращаем 200 OK
    return {
        "status": "ok",
        "message": "Callback accepted",
        "request_id": request_id
    }


@router.get("/test")
async def test_endpoint():
    """Тестовый эндпоинт"""
    request_id = request_id_ctx.get()
    logger.info("🧪 TEST ENDPOINT CALLED", extra={"request_id": request_id, "layer": "router"})
    return {"status": "ok", "service": "alpha_hook", "request_id": request_id}