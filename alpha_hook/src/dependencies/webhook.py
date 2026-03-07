# alpha_hook/src/dependencies/webhook.py
"""
Зависимости для валидации вебхуков
"""

from fastapi import Depends, Request
from loguru import logger
from typing import Optional

from src.schemas.webhook import WebhookPayload
from src.middleware.request_id import request_id_ctx
from src.exceptions.webhook import ValidationError


async def get_validated_payload(request: Request) -> Optional[WebhookPayload]:
    """
    Dependency: парсит и валидирует входящий payload.

    Returns:
        WebhookPayload если валидация успешна
        None если валидация не прошла
    """
    request_id = request_id_ctx.get()
    content_type = request.headers.get("content-type", "")

    # Логируем начало валидации
    logger.debug(
        "🔍 STARTING PAYLOAD VALIDATION",
        extra={
            "request_id": request_id,
            "content_type": content_type,
            "layer": "dependencies"
        }
    )

    try:
        # Парсим тело запроса
        body = await request.body()
        body_text = body.decode('utf-8', errors='ignore')

        # Определяем формат и парсим
        if "application/json" in content_type:
            data = await request.json()
            logger.debug("📦 Parsed as JSON", extra={"request_id": request_id, "layer": "dependencies"})

        elif "application/x-www-form-urlencoded" in content_type:
            form = await request.form()
            data = dict(form)
            # Конвертируем status в int
            if "status" in data and isinstance(data["status"], str):
                data["status"] = int(data["status"])
            logger.debug("📦 Parsed as form-urlencoded", extra={"request_id": request_id, "layer": "dependencies"})

        else:
            # Неподдерживаемый тип
            logger.warning(
                "⚠️ UNSUPPORTED CONTENT TYPE",
                extra={
                    "request_id": request_id,
                    "content_type": content_type,
                    "layer": "dependencies"
                }
            )
            return None

        # Валидация через Pydantic
        logger.debug(
            "🔧 Running Pydantic validation",
            extra={
                "request_id": request_id,
                "fields": list(data.keys()),
                "layer": "dependencies"
            }
        )

        payload = WebhookPayload(**data)

        # Успешная валидация
        logger.info(
            "✅ PAYLOAD VALIDATION SUCCESSFUL",
            extra={
                "request_id": request_id,
                "orderNumber": payload.orderNumber,
                "mdOrder": payload.mdOrder,
                "operation": payload.operation,
                "status": payload.status,
                "has_amount": payload.amount is not None,
                "layer": "dependencies"
            }
        )

        return payload

    except Exception as e:
        # Ошибка валидации
        logger.warning(
            "❌ PAYLOAD VALIDATION FAILED",
            extra={
                "request_id": request_id,
                "error": str(e),
                "error_type": type(e).__name__,
                "content_type": content_type,
                "body_preview": body_text[:200] if 'body_text' in locals() else None,
                "layer": "dependencies"
            }
        )
        return None