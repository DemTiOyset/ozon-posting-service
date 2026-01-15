from typing import TypeVar, Type, Generic, Mapping, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from application.db import async_session_maker
from application.orders.models.orders import Orders

class OrderRepository:
    @staticmethod
    async def get_order_items_by_posting_number(
            posting_number: int,
    ) -> Orders:
        async with async_session_maker() as session:
            async with session.begin():
                stmt = (select(Orders)
                        .where(Orders.posting_number == posting_number)
                        )

                result = await session.execute(stmt)
                orders = result.scalars().all()

                return orders


