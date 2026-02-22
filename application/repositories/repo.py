from datetime import datetime
from typing import List

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from application.database.models.order_items import OrderItems
from application.database.models.orders import Orders


class OrderRepository:
    @staticmethod
    async def get_order_items_by_posting_number(
            session: AsyncSession,
            posting_number: str,
    ) -> Orders:
        stmt = (select(OrderItems)
                .where(posting_number == posting_number)
                )

        result = await session.execute(stmt)
        orders = result.scalars().all()

        return orders

    @staticmethod
    async def get_one_or_none_by_posting_number(
            session: AsyncSession,
            posting_number: str
    ):
        stmt = (select(Orders)
        .where(
            Orders.posting_number == posting_number
            )
        )

        result = await session.execute(stmt)
        orders_shipment_date = result.scalar_one_or_none()

        return orders_shipment_date

    @staticmethod
    async def create_order_with_items(
            session: AsyncSession,
            order: Orders,
            order_items: List[OrderItems],
    ) -> Orders:
        order.items = order_items

        session.add(order)
        await session.flush()

        return order

    @staticmethod
    async def update_order_shipment_date(
            session: AsyncSession,
            posting_number: str,
            shipment_date: datetime,
    ) -> Orders:
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == posting_number
            )
            .values(shipment_date=shipment_date)
            .returning(Orders)
        )

        result = await session.execute(stmt)
        updated_orders = result.scalars().all()
        await session.flush()

        return updated_orders

    @staticmethod
    async def update_order_status(
            session: AsyncSession,
            posting_number: str,
            status: str,
    ) -> Orders:
        
        stmt = (
            update(Orders)
            .where(
                Orders.posting_number == posting_number,
            )
            .values(status=status)
            .returning(Orders)
        )

        result = await session.execute(stmt)
        orders = result.scalars().all()
        await session.flush()

        return orders

    @staticmethod
    async def reduce_item_quantity(
            session: AsyncSession,
            posting_number: str,
            sku: int,
            quantity_to_reduce: int,
    ) -> OrderItems:
        """
        Уменьшает quantity на указанное значение.
        Бросает исключение, если результат будет отрицательным.
        """
        # UPDATE с относительным изменением
        stmt = (
            update(OrderItems)
            .where(
                posting_number == posting_number,
                sku == sku,
                OrderItems.quantity >= quantity_to_reduce,  # защита от отрицательных
            )
            .values(
                quantity=OrderItems.quantity - quantity_to_reduce,
                quantity_cancelled=OrderItems.quantity_cancelled + quantity_to_reduce,
            )
            .returning(OrderItems.quantity)
        )

        result = await session.execute(stmt)
        updated_item = result.scalar_one_or_none()

        if not updated_item:
            # Либо записи нет, либо quantity недостаточно
            raise ValueError(
                f"Cannot reduce quantity: item not found or insufficient quantity"
            )

        await session.flush()  # применить изменения в текущей транзакции
        return updated_item

    @staticmethod
    async def establish_cancelled(
            session: AsyncSession,
            posting_number: str,
            sku: int
    ) -> OrderItems:
        stmt = (
            update(OrderItems)
            .where(
                OrderItems.order_posting_number==posting_number,
                OrderItems.sku == sku,
                   )
            .values(
                is_returned=True
                    )
            .returning(OrderItems)
        )

        result = await session.execute(stmt)
        updated_item = result.scalar_one_or_none()
        await session.flush()  # применить изменения в текущей транзакции
        return updated_item




