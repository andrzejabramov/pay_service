from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime

# === Channels ===


class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    type: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="email, telegram, whatsapp, sms, webhook",
    )
    address: str = Field(..., min_length=1)
    config: Optional[Dict[str, Any]] = Field(default_factory=dict)


class ChannelUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    type: Optional[str] = Field(None, max_length=50)
    address: Optional[str] = None
    config: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


class ChannelRead(BaseModel):
    id: UUID
    name: str
    type: str
    address: str
    config: Optional[Dict[str, Any]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


# === Templates ===


class TemplateVariable(BaseModel):
    name: str
    type: str  # date, int, money, string, datetime


class TemplateCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    channel_type: str = Field(..., min_length=1, max_length=50)
    body_template: str = Field(..., min_length=1)
    subject_template: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = Field(default_factory=list)


class TemplateUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    channel_type: Optional[str] = Field(None, max_length=50)
    body_template: Optional[str] = None
    subject_template: Optional[str] = None
    variables: Optional[List[TemplateVariable]] = None
    is_active: Optional[bool] = None


class TemplateRead(BaseModel):
    id: UUID
    name: str
    channel_type: str
    subject_template: Optional[str] = None
    body_template: str
    variables: Optional[List[Dict[str, Any]]] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
