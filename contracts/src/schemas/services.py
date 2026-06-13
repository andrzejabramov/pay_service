from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
import re


class ServiceBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Название услуги")
    code: str = Field(
        ..., min_length=1, max_length=64, description="Уникальный код (snake_case)"
    )
    category: Optional[str] = Field(
        None, max_length=100, description="Категория услуги"
    )
    description: Optional[str] = Field(None, description="Описание для договоров и UI")
    settings: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="Гибкие настройки услуги"
    )

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: str) -> str:
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(
                "Code must be lowercase snake_case (latin letters, digits, underscores), starting with a letter"
            )
        return v


class ServiceCreate(ServiceBase):
    pass


class ServiceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    code: Optional[str] = Field(None, min_length=1, max_length=64)
    category: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    settings: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None

    @field_validator("code")
    @classmethod
    def validate_code(cls, v: Optional[str]) -> Optional[str]:
        if v is not None and not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(
                "Code must be lowercase snake_case (latin letters, digits, underscores), starting with a letter"
            )
        return v


class ServiceRead(ServiceBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
