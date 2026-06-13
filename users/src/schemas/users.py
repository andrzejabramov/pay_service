from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any, List
from datetime import datetime
from uuid import UUID
import phonenumbers


class UserBase(BaseModel):
    is_active: Optional[bool] = None
    profile: Optional[Dict[str, Any]] = None


class UserCreate(UserBase):
    pass


class UserUpdate(BaseModel):
    is_active: Optional[bool] = None
    profile: Optional[Dict[str, Any]] = None


class UserRead(UserBase):
    id: UUID
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    profile: Optional[Dict[str, Any]] = None
    model_config = {"from_attributes": True}


class UserReadExtended(UserRead):
    contacts: Dict[str, str] = Field(default_factory=dict)
    groups: List[str] = Field(default_factory=list)


class BulkUserItem(BaseModel):
    phone: str
    external_id: Optional[str] = None

    @field_validator("phone")
    @classmethod
    def validate_phone(cls, v: str) -> str:
        try:
            parsed = phonenumbers.parse(v, None)
            if not phonenumbers.is_valid_number(parsed):
                raise ValueError("Invalid phone")
            return phonenumbers.format_number(
                parsed, phonenumbers.PhoneNumberFormat.E164
            )
        except Exception as e:
            raise ValueError(f"Invalid phone format: {e}")


class BulkCreateRequest(BaseModel):
    interface: str
    users: List[BulkUserItem] = Field(..., min_length=1, max_length=1000)


class BulkCreateResult(BaseModel):
    created: int
    skipped: int
    errors: List[dict]


class UserBulkCreateRow(BaseModel):
    phone: str = Field(
        ..., min_length=10, max_length=15, pattern=r"^\+?[0-9\s\-\(\)]+$"
    )
    user_groups: str = Field(..., min_length=1)


class UploadResult(BaseModel):
    success_count: int
    error_count: int
    errors: List[str] = Field(default_factory=list)


# ============================================================
# 👇 ИСПРАВЛЕННЫЙ БЛОК ДЛЯ UserDetailRead
# ============================================================


class UserGroupItem(BaseModel):
    """Группа пользователя (роль)."""

    id: int  # в БД это smallint → int в Python
    name: str


class UserContactItem(BaseModel):
    """Контакт пользователя (телефон, email и т.д.)."""

    id: UUID
    type: str  # имя типа контакта (phone, email, second_login)
    value: str


class UserDetailRead(BaseModel):
    """
    Полная информация о пользователе с контактами и группами.
    Возвращается функцией accounts.get_user_by_identifier_v1.
    """

    id: UUID
    created_at: datetime
    updated_at: Optional[datetime] = None
    is_active: bool
    profile: Optional[dict[str, Any]] = None
    groups: List[UserGroupItem] = Field(default_factory=list)
    contacts: List[UserContactItem] = Field(default_factory=list)

    model_config = {"from_attributes": True}
