from typing import List

from sqlalchemy import select, update

from application.db import async_session_maker
from application.orders.models.orders import Orders
from application.orders.shemas.orders import OrderDTO


async def _create_order_with_items(
        orders: List[Orders],
) -> List[Orders]:

    async with async_session_maker() as session:
        async with session.begin():
            for order in orders:
                session.add(order)

                await session.flush()
                await session.refresh(order)

            stmt = (select(Orders)
                    .where(Orders.posting_number == orders.posting_number)
                    )

            result = await session.execute(stmt)
            orders = result.scalars().all()

            return orders


async def _cancel_order_items(
        orders: Orders,
) -> Orders:

    async with async_session_maker() as session:
        async with session.begin():
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

            result = await session.execute(stmt)
            updated_orders = result.scalars().all()

            return updated_orders



async def _update_order_shipment_date(
        orders: Orders,
) -> Orders:

    async with async_session_maker() as session:
        async with session.begin():
            stmt = (
                update(Orders)
                .where(
                    Orders.posting_number == orders.posting_number,
                    Orders.is_returned.is_(False),
                )
                .values(shipment_date=orders.shipment_date)
                .returning(Orders)
            )

            result = await session.execute(stmt)
            updated_orders = result.scalars().all()

            return updated_orders


async def _update_order_status(
        orders: Orders,
) -> Orders:

    async with async_session_maker() as session:
        async with session.begin():
            stmt = (
                update(Orders)
                .where(
                    Orders.posting_number == orders.posting_number,
                    Orders.is_returned.is_(False),
                )
                .values(status=orders.status)
                .returning(Orders)
            )

            result = await session.execute(stmt)
            orders = result.scalars().all()

            return orders


async def _update_order_delivery_date_items(
        orders: Orders,
) -> Orders:

    async with async_session_maker() as session:
        async with session.begin():
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

            result = await session.execute(stmt)
            updated_orders = result.scalars().all()

            return updated_orders


def __dto_to_order(dto: OrderDTO) -> Orders:
    data = dto.model_dump(exclude_none=True)
    return Orders(**data)

