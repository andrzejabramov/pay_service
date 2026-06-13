from fastapi import APIRouter, Depends, HTTPException, status, Query
from asyncpg import Pool
from asyncpg.exceptions import UniqueViolationError
from typing import List, Optional

from src.db.pools import get_write_pool, get_read_pool
from src.services.services import ServiceCrudService
from src.schemas.services import ServiceCreate, ServiceUpdate, ServiceRead
from src.exceptions.exceptions import NotFoundError

router = APIRouter(tags=["Services"])


def get_service_read(pool: Pool = Depends(get_read_pool)) -> ServiceCrudService:
    return ServiceCrudService(pool)


def get_service_write(pool: Pool = Depends(get_write_pool)) -> ServiceCrudService:
    return ServiceCrudService(pool)


@router.post("/", response_model=ServiceRead, status_code=status.HTTP_201_CREATED)
async def create_service(
    data: ServiceCreate,
    service: ServiceCrudService = Depends(get_service_write),
):
    try:
        return await service.create(data)
    except UniqueViolationError:
        raise HTTPException(
            status_code=409, detail=f"Service with code '{data.code}' already exists"
        )
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", response_model=List[ServiceRead])
async def list_services(
    only_active: bool = Query(True, description="Только активные услуги"),
    category: Optional[str] = Query(None, description="Фильтр по категории"),
    service: ServiceCrudService = Depends(get_service_read),
):
    return await service.list_all(only_active=only_active, category=category)


@router.get("/{service_id}", response_model=ServiceRead)
async def get_service(
    service_id: str,
    service: ServiceCrudService = Depends(get_service_read),
):
    try:
        return await service.get_by_id(service_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Service", service_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/{service_id}", response_model=ServiceRead)
async def update_service(
    service_id: str,
    data: ServiceUpdate,
    service: ServiceCrudService = Depends(get_service_write),
):
    try:
        return await service.update(service_id, data)
    except UniqueViolationError:
        raise HTTPException(
            status_code=409, detail=f"Service with this code already exists"
        )
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Service", service_id)
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{service_id}", response_model=ServiceRead)
async def deactivate_service(
    service_id: str,
    service: ServiceCrudService = Depends(get_service_write),
):
    """Мягкое удаление (is_active = false)"""
    try:
        return await service.deactivate(service_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Service", service_id)
        raise HTTPException(status_code=500, detail=str(e))
