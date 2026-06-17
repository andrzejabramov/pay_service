import json
from asyncpg import Pool
from typing import List
from src.schemas.organisations import (
    OrganisationCreate,
    OrganisationUpdate,
    OrganisationRead,
)
from src.utils.json_utils import maybe_json_dumps, maybe_json_loads


class OrganisationService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create(self, data: OrganisationCreate) -> OrganisationRead:
        requisites_json = maybe_json_dumps(data.requisites.model_dump())
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM organisations.create_organisation($1, $2::jsonb)",
                data.name_org,
                requisites_json,
            )
        return self._to_read(row)

    async def get_by_id(self, org_id: str) -> OrganisationRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM organisations.get_organisation_by_id($1::uuid)", org_id
            )
        return self._to_read(row)

    async def list_all(self) -> List[OrganisationRead]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM organisations.list_organisations()")
        return [self._to_read(row) for row in rows]

    async def update(self, org_id: str, data: OrganisationUpdate) -> OrganisationRead:
        requisites_json = (
            maybe_json_dumps(data.requisites.model_dump()) if data.requisites else None
        )
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM organisations.update_organisation($1::uuid, $2, $3::jsonb)",
                org_id,
                data.name_org,
                requisites_json,
            )
        return self._to_read(row)

    async def delete(self, org_id: str) -> None:
        async with self.pool.acquire() as conn:
            await conn.execute(
                "SELECT organisations.delete_organisation($1::uuid)", org_id
            )

    @staticmethod
    def _to_read(row) -> OrganisationRead:
        d = dict(row)
        req = d.get("requisites")
        if isinstance(req, str):
            req = json.loads(req)
        d["requisites"] = req
        return OrganisationRead(**d)
