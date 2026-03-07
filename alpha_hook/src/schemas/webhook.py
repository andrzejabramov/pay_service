# alpha_hook/src/schemas/webhook.py
from pydantic import BaseModel, ConfigDict, Field, field_validator
from typing import Optional
import uuid


class WebhookPayload(BaseModel):
    """
    Схема входящего webhook от Альфа-Банка.

    Банк шлёт: application/x-www-form-urlencoded или application/json
    Поля: mdOrder (UUID), orderNumber (Driver ID), operation, status, checksum, ...
    """
    model_config = ConfigDict(extra="allow")  # разрешить доп. поля от банка

    # === Обязательные поля (как шлёт банк) ===
    orderNumber: str = Field(..., description="ID водителя/терминала из QR-кода")
    mdOrder: str = Field(..., description="ID транзакции в шлюзе банка (UUID)")
    operation: str = Field(..., description="Тип события: deposited, approved, etc.")
    status: int = Field(..., description="1=успех, 0=ошибка")  # ← int, не str!
    checksum: str = Field(..., description="Контрольная сумма для валидации")

    # === Опциональные поля (запросить в поддержке) ===
    amount: Optional[int] = Field(None, description="Сумма в копейках")
    currency: Optional[str] = Field(None, description="Валюта (RUB)")
    approvalCode: Optional[str] = Field(None, description="Код авторизации")
    paymentRefNum: Optional[str] = Field(None, description="RRN от эквайера")
    paymentDate: Optional[str] = Field(None, description="Дата оплаты (ISO 8601)")

    # === Валидаторы ===
    @field_validator('mdOrder')
    @classmethod
    def validate_md_order_uuid(cls, v: str) -> str:
        """Проверить, что mdOrder — валидный UUID"""
        try:
            uuid.UUID(v)
            return v
        except ValueError:
            raise ValueError(f"mdOrder must be a valid UUID, got: {v}")

    @field_validator('status')
    @classmethod
    def validate_status(cls, v: int) -> int:
        """Проверить, что status — 0 или 1"""
        if v not in (0, 1):
            raise ValueError(f"status must be 0 or 1, got: {v}")
        return v

    # === Вспомогательные свойства ===
    @property
    def amount_rub(self) -> Optional[float]:
        """Конвертация копеек → рубли"""
        return self.amount / 100.0 if self.amount else None

    @property
    def is_successful_payment(self) -> bool:
        """Успешная оплата = deposited + status=1"""
        return self.operation == "deposited" and self.status == 1

    @property
    def driver_id(self) -> str:
        """Alias для orderNumber — ваш идентификатор водителя"""
        return self.orderNumber

    @property
    def transaction_uuid(self) -> uuid.UUID:
        """Конвертация mdOrder (str) → UUID для сохранения в id_uuid"""
        return uuid.UUID(self.mdOrder)


class ApiResponse(BaseModel):
    """Стандартный ответ API"""
    status: str
    message: Optional[str] = None