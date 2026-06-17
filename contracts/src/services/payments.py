import json
from asyncpg import Pool
from typing import List
from src.schemas.payments import MerchantCreate, MerchantUpdate, MerchantRead
from src.utils.json_utils import maybe_json_dumps, maybe_json_loads


class PaymentService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    async def create_merchant(self, data: MerchantCreate) -> MerchantRead:
        config_json = maybe_json_dumps(data.config)
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payments.create_merchant($1, $2, $3::jsonb, $4)",
                data.name,
                data.type,
                config_json,
                data.legacy_id,
            )
        return self._to_read(row)

    async def list_merchants(self, only_active: bool = True) -> List[MerchantRead]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM payments.list_merchants($1)", only_active
            )
        return [self._to_read(r) for r in rows]

    async def get_merchant(self, merchant_id: str) -> MerchantRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payments.get_merchant_by_id($1::uuid)", merchant_id
            )
        return self._to_read(row)

    async def update_merchant(
        self, merchant_id: str, data: MerchantUpdate
    ) -> MerchantRead:
        config_json = maybe_json_dumps(data.config) if data.config else None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payments.update_merchant($1::uuid, $2, $3, $4::jsonb, $5)",
                merchant_id,
                data.name,
                data.type,
                config_json,
                data.is_active,
            )
        return self._to_read(row)

    async def deactivate_merchant(self, merchant_id: str) -> MerchantRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM payments.deactivate_merchant($1::uuid)", merchant_id
            )
        return self._to_read(row)

    @staticmethod
    def _to_read(row) -> MerchantRead:
        d = dict(row)
        d["config"] = maybe_json_loads(d.get("config"))
        return MerchantRead(**d)
