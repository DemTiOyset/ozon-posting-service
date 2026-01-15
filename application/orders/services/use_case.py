from http.client import HTTPException

from application.orders.integrations.market.client import get_order
from application.orders.repo import OrderRepository
from application.orders.services.manage_repo import _create_order_with_items
from application.orders.services.manage_transformation import _transforming_order_creation_data
from application.orders.shemas.notification import OrderCreatedNotificationDTO


async def handle_order_created(
        notification: OrderCreatedNotificationDTO
):
    order_from_market = await get_order(..., ...)
    order_from_db = \
        await OrderRepository.get_order_items_by_posting_number(notification.posting_number)

    if order_from_db:
        raise ...

    order_items_dto = await _transforming_order_creation_data(
        notification=notification,
        order_data=order_from_market
    )

    dto_to_model = [dto for dto in order_items_dto]

    creation_order_items_in_db = await _create_order_with_items(dto_to_model)

    return {"message": "ok"}





