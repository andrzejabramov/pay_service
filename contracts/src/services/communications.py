import json
from asyncpg import Pool
from typing import List, Optional
from src.schemas.communications import (
    ChannelCreate,
    ChannelUpdate,
    ChannelRead,
    TemplateCreate,
    TemplateUpdate,
    TemplateRead,
)
from src.utils.json_utils import maybe_json_dumps, maybe_json_loads


class CommunicationService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    # === Channels ===

    async def create_channel(self, data: ChannelCreate) -> ChannelRead:
        config_json = maybe_json_dumps(data.config)
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.create_channel($1, $2, $3, $4::jsonb)",
                data.name,
                data.type,
                data.address,
                config_json,
            )
        return self._to_channel(row)

    async def list_channels(self, only_active: bool = True) -> List[ChannelRead]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM communications.list_channels($1)", only_active
            )
        return [self._to_channel(r) for r in rows]

    async def get_channel(self, channel_id: str) -> ChannelRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.get_channel($1::uuid)", channel_id
            )
        return self._to_channel(row)

    async def update_channel(self, channel_id: str, data: ChannelUpdate) -> ChannelRead:
        config_json = maybe_json_dumps(data.config) if data.config else None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.update_channel($1::uuid, $2, $3, $4, $5::jsonb, $6)",
                channel_id,
                data.name,
                data.type,
                data.address,
                config_json,
                data.is_active,
            )
        return self._to_channel(row)

    async def deactivate_channel(self, channel_id: str) -> ChannelRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.deactivate_channel($1::uuid)", channel_id
            )
        return self._to_channel(row)

    # === Templates ===

    async def create_template(self, data: TemplateCreate) -> TemplateRead:
        vars_json = (
            maybe_json_dumps([v.model_dump() for v in data.variables])
            if data.variables
            else None
        )
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.create_template($1, $2, $3, $4, $5::jsonb)",
                data.name,
                data.channel_type,
                data.body_template,
                data.subject_template,
                vars_json,
            )
        return self._to_template(row)

    async def list_templates(
        self, only_active: bool = True, channel_type: Optional[str] = None
    ) -> List[TemplateRead]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM communications.list_templates($1, $2)",
                only_active,
                channel_type,
            )
        return [self._to_template(r) for r in rows]

    async def get_template(self, template_id: str) -> TemplateRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.get_template($1::uuid)", template_id
            )
        return self._to_template(row)

    async def update_template(
        self, template_id: str, data: TemplateUpdate
    ) -> TemplateRead:
        vars_json = (
            maybe_json_dumps([v.model_dump() for v in data.variables])
            if data.variables
            else None
        )
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.update_template($1::uuid, $2, $3, $4, $5, $6::jsonb, $7)",
                template_id,
                data.name,
                data.channel_type,
                data.subject_template,
                data.body_template,
                vars_json,
                data.is_active,
            )
        return self._to_template(row)

    async def deactivate_template(self, template_id: str) -> TemplateRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM communications.deactivate_template($1::uuid)",
                template_id,
            )
        return self._to_template(row)

    # === Helpers ===

    @staticmethod
    def _to_channel(row) -> ChannelRead:
        d = dict(row)
        d["config"] = maybe_json_loads(d.get("config"))
        return ChannelRead(**d)

    @staticmethod
    def _to_template(row) -> TemplateRead:
        d = dict(row)
        d["variables"] = maybe_json_loads(d.get("variables"))
        return TemplateRead(**d)
