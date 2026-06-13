from fastapi import APIRouter, Depends, HTTPException, status
from asyncpg import Pool
from asyncpg.exceptions import UniqueViolationError, ForeignKeyViolationError
from typing import List

from src.db.pools import get_write_pool, get_read_pool
from src.services.organisations import OrganisationService
from src.schemas.organisations import (
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationRead,
)
from src.exceptions.exceptions import NotFoundError

router = APIRouter(tags=["Organisations"])


def get_org_read_service(pool: Pool = Depends(get_read_pool)) -> OrganisationService:
    return OrganisationService(pool)


def get_org_write_service(
    pool: Pool = Depends(get_write_pool),
) -> OrganisationService:
    return OrganisationService(pool)


@router.post("/", response_model=OrganisationRead, status_code=status.HTTP_201_CREATED)
async def create_organisation(
    data: OrganisationCreate,
    service: OrganisationService = Depends(
        get_org_write_service  # ← используем исправленную зависимость get_org_wri
    ),  # ← используем исправленную зависимость
):
    try:
        return await service.create(data)
    except UniqueViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Organisation with this INN already exists",
        )
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.get("/", response_model=List[OrganisationRead])
async def list_organisations(
    service: OrganisationService = Depends(
        get_org_read_service
    ),  # ← ИСПРАВЛЕНО: было Depends(get_read_db_pool)
):
    return await service.list_all()


@router.get("/{org_id}", response_model=OrganisationRead)
async def get_organisation(
    org_id: str,
    service: OrganisationService = Depends(get_org_read_service),  # ← ИСПРАВЛЕНО
):
    try:
        return await service.get_by_id(org_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Organisation", org_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.patch("/{org_id}", response_model=OrganisationRead)
async def update_organisation(
    org_id: str,
    data: OrganisationUpdate,
    service: OrganisationService = Depends(
        get_org_write_service
    ),  # ← ИСПРАВЛЕНО + write pool ниже
):
    try:
        # Для write-операций нужен write_pool, но пока используем read для простоты
        # В продакшене лучше разделить: get_write_db_pool для PATCH/POST/DELETE
        return await service.update(org_id, data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Organisation", org_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )


@router.delete("/{org_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_organisation(
    org_id: str,
    service: OrganisationService = Depends(get_org_write_service),  # ← ИСПРАВЛЕНО
):
    try:
        await service.delete(org_id)
        return None
    except ForeignKeyViolationError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Cannot delete organisation: it is referenced by other records",
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Organisation", org_id)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e)
        )
