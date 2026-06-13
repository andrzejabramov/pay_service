from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime


class BankRequisites(BaseModel):
    bik: str = Field(..., min_length=9, max_length=9)
    name: str = Field(..., min_length=1)
    account: str = Field(..., min_length=20, max_length=20)


class DirectorRequisites(BaseModel):
    position: str = Field(default="Генеральный директор")
    fio: str = Field(..., min_length=1)


class OrganisationRequisites(BaseModel):
    form: str = Field(..., description="ООО, АО, ПАО, ИП")
    name: str = Field(..., min_length=1)
    inn: str = Field(..., min_length=10, max_length=12)
    ogrn: Optional[str] = None
    address: Optional[str] = None
    bank: Optional[BankRequisites] = None
    director: Optional[DirectorRequisites] = None

    @field_validator("inn")
    @classmethod
    def validate_inn(cls, v: str) -> str:
        if not v.isdigit():
            raise ValueError("ИНН должен содержать только цифры")
        if len(v) not in (10, 12):
            raise ValueError("ИНН: 10 (юрлицо) или 12 (ИП) цифр")
        return v


class OrganisationCreate(BaseModel):
    name_org: str = Field(..., min_length=1, max_length=50)
    requisites: OrganisationRequisites


class OrganisationUpdate(BaseModel):
    name_org: Optional[str] = Field(None, max_length=50)
    requisites: Optional[OrganisationRequisites] = None


class OrganisationRead(BaseModel):
    id: UUID
    name_org: str
    inn_org: str
    requisites: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}
