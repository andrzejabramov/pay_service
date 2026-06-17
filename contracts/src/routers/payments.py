from fastapi import APIRouter, Depends, HTTPException, status, Query
from asyncpg import Pool
from typing import List

from src.db.pools import get_write_pool, get_read_pool
from src.services.payments import PaymentService
from src.schemas.payments import MerchantCreate, MerchantUpdate, MerchantRead
from src.exceptions.exceptions import NotFoundError

router = APIRouter(tags=["Payments"])


def _read_svc(pool: Pool = Depends(get_read_pool)) -> PaymentService:
    return PaymentService(pool)


def _write_svc(pool: Pool = Depends(get_write_pool)) -> PaymentService:
    return PaymentService(pool)


@router.post(
    "/merchants", response_model=MerchantRead, status_code=status.HTTP_201_CREATED
)
async def create_merchant(
    data: MerchantCreate, svc: PaymentService = Depends(_write_svc)
):
    try:
        return await svc.create_merchant(data)
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/merchants", response_model=List[MerchantRead])
async def list_merchants(
    only_active: bool = Query(True), svc: PaymentService = Depends(_read_svc)
):
    return await svc.list_merchants(only_active)


@router.get("/merchants/{merchant_id}", response_model=MerchantRead)
async def get_merchant(merchant_id: str, svc: PaymentService = Depends(_read_svc)):
    try:
        return await svc.get_merchant(merchant_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Merchant", merchant_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/merchants/{merchant_id}", response_model=MerchantRead)
async def update_merchant(
    merchant_id: str, data: MerchantUpdate, svc: PaymentService = Depends(_write_svc)
):
    try:
        return await svc.update_merchant(merchant_id, data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Merchant", merchant_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/merchants/{merchant_id}", response_model=MerchantRead)
async def deactivate_merchant(
    merchant_id: str, svc: PaymentService = Depends(_write_svc)
):
    try:
        return await svc.deactivate_merchant(merchant_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Merchant", merchant_id)
        raise HTTPException(status_code=500, detail=str(e))
