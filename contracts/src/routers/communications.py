from fastapi import APIRouter, Depends, HTTPException, status, Query
from asyncpg import Pool
from typing import List, Optional

from src.db.pools import get_write_pool, get_read_pool
from src.services.communications import CommunicationService
from src.schemas.communications import (
    ChannelCreate,
    ChannelUpdate,
    ChannelRead,
    TemplateCreate,
    TemplateUpdate,
    TemplateRead,
)
from src.exceptions.exceptions import NotFoundError

router = APIRouter(tags=["Communications"])


def _read_svc(pool: Pool = Depends(get_read_pool)) -> CommunicationService:
    return CommunicationService(pool)


def _write_svc(pool: Pool = Depends(get_write_pool)) -> CommunicationService:
    return CommunicationService(pool)


# === Channels ===


@router.post(
    "/channels", response_model=ChannelRead, status_code=status.HTTP_201_CREATED
)
async def create_channel(
    data: ChannelCreate, svc: CommunicationService = Depends(_write_svc)
):
    try:
        return await svc.create_channel(data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/channels", response_model=List[ChannelRead])
async def list_channels(
    only_active: bool = Query(True), svc: CommunicationService = Depends(_read_svc)
):
    return await svc.list_channels(only_active)


@router.get("/channels/{channel_id}", response_model=ChannelRead)
async def get_channel(channel_id: str, svc: CommunicationService = Depends(_read_svc)):
    try:
        return await svc.get_channel(channel_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Channel", channel_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/channels/{channel_id}", response_model=ChannelRead)
async def update_channel(
    channel_id: str,
    data: ChannelUpdate,
    svc: CommunicationService = Depends(_write_svc),
):
    try:
        return await svc.update_channel(channel_id, data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Channel", channel_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/channels/{channel_id}", response_model=ChannelRead)
async def deactivate_channel(
    channel_id: str, svc: CommunicationService = Depends(_write_svc)
):
    try:
        return await svc.deactivate_channel(channel_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Channel", channel_id)
        raise HTTPException(status_code=500, detail=str(e))


# === Templates ===


@router.post(
    "/templates", response_model=TemplateRead, status_code=status.HTTP_201_CREATED
)
async def create_template(
    data: TemplateCreate, svc: CommunicationService = Depends(_write_svc)
):
    try:
        return await svc.create_template(data)
    except Exception as e:
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/templates", response_model=List[TemplateRead])
async def list_templates(
    only_active: bool = Query(True),
    channel_type: Optional[str] = Query(None),
    svc: CommunicationService = Depends(_read_svc),
):
    return await svc.list_templates(only_active, channel_type)


@router.get("/templates/{template_id}", response_model=TemplateRead)
async def get_template(
    template_id: str, svc: CommunicationService = Depends(_read_svc)
):
    try:
        return await svc.get_template(template_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Template", template_id)
        raise HTTPException(status_code=500, detail=str(e))


@router.patch("/templates/{template_id}", response_model=TemplateRead)
async def update_template(
    template_id: str,
    data: TemplateUpdate,
    svc: CommunicationService = Depends(_write_svc),
):
    try:
        return await svc.update_template(template_id, data)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Template", template_id)
        if "already exists" in str(e).lower():
            raise HTTPException(status_code=409, detail=str(e))
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/templates/{template_id}", response_model=TemplateRead)
async def deactivate_template(
    template_id: str, svc: CommunicationService = Depends(_write_svc)
):
    try:
        return await svc.deactivate_template(template_id)
    except Exception as e:
        if "not found" in str(e).lower():
            raise NotFoundError("Template", template_id)
        raise HTTPException(status_code=500, detail=str(e))
