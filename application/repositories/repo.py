from datetime import datetime
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.database.models.orders import Orders

class OrderRepository:
    def __init__(self, session: AsyncSession):
        self._session = session

    async def get_order_items_by_posting_number(
            self,
            posting_number: str,
    ) -> Orders:
        stmt = (select(Orders)
                .where(Orders.posting_number == posting_number)
                )

        result = await self._session.execute(stmt)
        orders = result.scalars().all()

        return orders

    
    async def get_first_order_by_posting_number(
            self,
            posting_number: str
    ):
        stmt = (select(Orders)
        .where(
            Orders.posting_number == posting_number
            )
        )

        result = await self._session.execute(stmt)
        orders_shipment_date = result.scalars().first()

        return orders_shipment_date

    
    async def create_order_with_items(
            self,
            orders: List[Orders],
    ) -> List[Orders]:
        
        self._session.add_all(orders)
        await self._session.flush()

        return orders

    
    async def cancel_order_items(
            self,
            orders: Orders,
    ) -> Orders:
        
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == orders.posting_number,
                Orders.sku == orders.sku,
                Orders.is_returned.is_(False),
            )
            .values(is_returned=True)
            .returning(Orders)
        )

        result = await self._session.execute(stmt)
        updated_orders = result.scalars().all()

        return updated_orders

    
    async def update_order_shipment_date(
            self,
            posting_number: str,
            shipment_date: datetime,
    ) -> Orders:
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == posting_number,
                Orders.is_returned.is_(False),
            )
            .values(shipment_date=shipment_date)
            .returning(Orders)
        )

        result = await self._session.execute(stmt)
        updated_orders = result.scalars().all()

        return updated_orders

    
    async def update_order_status(
            self,
            posting_number: str,
            status: str,
    ) -> Orders:
        
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == posting_number,
                Orders.is_returned.is_(False),
            )
            .values(status=status)
            .returning(Orders)
        )

        result = await self._session.execute(stmt)
        orders = result.scalars().all()

        return orders

    
    async def update_order_delivery_date_items(
            self,
            orders: Orders,
    ) -> Orders:
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == orders.posting_number,
                Orders.is_returned.is_(False),
            )
            .values(
                delivery_date_begin=orders.delivery_date_begin,
                delivery_date_end=orders.delivery_date_end,
            )
            .returning(Orders)
        )

        result = await self._session.execute(stmt)
        updated_orders = result.scalars().all()

        return updated_orders


