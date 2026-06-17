from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class MerchantCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(default="unknown", max_length=50)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    legacy_id: Optional[int] = Field(
        None, description="Старый idmerch из common.merchant"
    )


class MerchantUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class MerchantRead(BaseModel):
    id: UUID
    legacy_id: Optional[int] = None
    name: str
    type: str
    config: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
