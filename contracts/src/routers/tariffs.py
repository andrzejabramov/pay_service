from fastapi import APIRouter, Depends, HTTPException, status, Query
from asyncpg import Pool
from typing import List, Optional

from src.db.pools import get_write_pool, get_read_pool
from src.services.tariffs import TariffService
from src.schemas.tariffs import (
    CalculationTypeRead,
    TariffCreate,
    TariffUpdate,
    TariffRead,
)
from src.exceptions.exceptions import NotFoundError

router = APIRouter(tags=["Tariffs"])


def _read_svc(pool: Pool = Depends(get_read_pool)) -> TariffService:
    return TariffService(pool)


def _write_svc(pool: Pool = Depends(get_write_pool)) -> TariffService:
    return TariffService(pool)


# === Calculation Types ===


@router.get("/calculation-types", response_model=List[CalculationTypeRead])
async def list_calculation_types(svc: TariffService = Depends(_read_svc)):
    return await svc.list_calculation_types()


# === Tariffs ===


@router.post("/tariffs", response_model=TariffRead, status_code=status.HTTP_201_CREATED)
async def create_tariff(data: TariffCreate, svc: TariffService = Depends(_write_svc)):
    try:
        return await svc.create_tariff(data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Calculation type", str(data.calculation_type_id))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tariffs", response_model=List[TariffRead])
async def list_tariffs(
    only_active: bool = Query(True),
    calculation_type_id: Optional[int] = Query(None),
    svc: TariffService = Depends(_read_svc),
):
    return await svc.list_tariffs(only_active, calculation_type_id)


@router.get("/tariffs/{tariff_id}", response_model=TariffRead)
async def get_tariff(tariff_id: int, svc: TariffService = Depends(_read_svc)):
    try:
        return await svc.get_tariff(tariff_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Tariff", str(tariff_id))
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/tariffs/{tariff_id}", response_model=TariffRead)
async def update_tariff(
    tariff_id: int, data: TariffUpdate, svc: TariffService = Depends(_write_svc)
):
    try:
        return await svc.update_tariff(tariff_id, data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Tariff", str(tariff_id))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/tariffs/{tariff_id}", response_model=TariffRead)
async def deactivate_tariff(tariff_id: int, svc: TariffService = Depends(_write_svc)):
    try:
        return await svc.deactivate_tariff(tariff_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Tariff", str(tariff_id))
        raise HTTPException(status_code=500, detail=str(e))
