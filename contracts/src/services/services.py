import json
from asyncpg import Pool
from typing import List, Optional
from src.schemas.services import ServiceCreate, ServiceUpdate, ServiceRead
from src.utils.json_utils import maybe_json_dumps, maybe_json_loads


class ServiceCrudService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, data: ServiceCreate) -> ServiceRead:
        settings_json = maybe_json_dumps(data.settings) if data.settings else None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM services.create_service($1, $2, $3, $4, $5::jsonb)",
                data.name,
                data.code,
                data.category,
                data.description,
                settings_json,
            )
        return self._to_read(row)

    async def get_by_id(self, service_id: str) -> ServiceRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM services.get_service_by_id($1::uuid)", service_id
            )
        return self._to_read(row)

    async def list_all(
        self, only_active: bool = True, category: Optional[str] = None
    ) -> List[ServiceRead]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM services.list_services($1, $2)", only_active, category
            )
        return [self._to_read(row) for row in rows]

    async def update(self, service_id: str, data: ServiceUpdate) -> ServiceRead:
        settings_json = maybe_json_dumps(data.settings) if data.settings else None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM services.update_service($1::uuid, $2, $3, $4, $5, $6::jsonb, $7)",
                service_id,
                data.name,
                data.code,
                data.category,
                data.description,
                settings_json,
                data.is_active,
            )
        return self._to_read(row)

    async def deactivate(self, service_id: str) -> ServiceRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM services.deactivate_service($1::uuid)", service_id
            )
        return self._to_read(row)

    @staticmethod
    def _to_read(row) -> ServiceRead:
        d = dict(row)
        req = d.get("settings")
        if isinstance(req, str):
            req = json.loads(req)
        d["settings"] = req
        return ServiceRead(**d)
