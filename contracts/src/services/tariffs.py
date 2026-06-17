import json
from asyncpg import Pool
from typing import List
from src.schemas.tariffs import (
    CalculationTypeRead,
    TariffCreate,
    TariffUpdate,
    TariffRead,
)
from src.utils.json_utils import maybe_json_dumps, maybe_json_loads


class TariffService:
    def __init__(self, db_pool: Pool):
        self.pool = db_pool

    # === Calculation Types (read-only справочник) ===

    async def list_calculation_types(self) -> List[CalculationTypeRead]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch("SELECT * FROM tariffs.list_calculation_types()")
        return [CalculationTypeRead(**dict(r)) for r in rows]

    # === Tariffs CRUD ===

    async def create_tariff(self, data: TariffCreate) -> TariffRead:
        params_json = maybe_json_dumps(data.params)
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM tariffs.create_tariff($1, $2, $3::jsonb, $4, $5, $6)",
                data.name,
                data.calculation_type_id,
                params_json,
                data.valid_from,
                data.valid_to,
                data.priority,
            )
        return self._to_read(row)

    async def get_tariff(self, tariff_id: int) -> TariffRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow("SELECT * FROM tariffs.get_tariff($1)", tariff_id)
        return self._to_read(row)

    async def list_tariffs(
        self, only_active: bool = True, calculation_type_id: int | None = None
    ) -> List[TariffRead]:
        async with self.pool.acquire() as conn:
            rows = await conn.fetch(
                "SELECT * FROM tariffs.list_tariffs($1, $2)",
                only_active,
                calculation_type_id,
            )
        return [self._to_read(r) for r in rows]

    async def update_tariff(self, tariff_id: int, data: TariffUpdate) -> TariffRead:
        params_json = maybe_json_dumps(data.params) if data.params else None
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM tariffs.update_tariff($1, $2, $3, $4::jsonb, $5, $6, $7, $8)",
                tariff_id,
                data.name,
                data.calculation_type_id,
                params_json,
                data.valid_from,
                data.valid_to,
                data.priority,
                data.is_active,
            )
        return self._to_read(row)

    async def deactivate_tariff(self, tariff_id: int) -> TariffRead:
        async with self.pool.acquire() as conn:
            row = await conn.fetchrow(
                "SELECT * FROM tariffs.deactivate_tariff($1)", tariff_id
            )
        return self._to_read(row)

    @staticmethod
    def _to_read(row) -> TariffRead:
        d = dict(row)
        d["params"] = maybe_json_loads(d.get("params"))
        return TariffRead(**d)
