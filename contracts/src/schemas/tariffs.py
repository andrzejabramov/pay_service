from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from datetime import datetime


class CalculationTypeRead(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    formula_template: str
    priority: int
    created_at: datetime

    model_config = {"from_attributes": True}


class TariffCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    calculation_type_id: int = Field(..., gt=0)
    params: Dict[str, Any] = Field(default_factory=dict)
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    priority: int = Field(default=0, ge=0)


class TariffUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    calculation_type_id: Optional[int] = Field(None, gt=0)
    params: Optional[Dict[str, Any]] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    priority: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None


class TariffRead(BaseModel):
    id: int
    name: str
    calculation_type_id: int
    params: Dict[str, Any]
    valid_from: datetime
    valid_to: Optional[datetime] = None
    priority: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    # JOIN fields
    calc_type_name: Optional[str] = None
    formula_template: Optional[str] = None

    model_config = {"from_attributes": True}
