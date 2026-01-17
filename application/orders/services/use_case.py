import asyncio

from pydantic import ValidationError
from fastapi.responses import JSONResponse
from fastapi import status

from application.orders.integrations.market.client import get_order
from application.orders.repo import OrderRepository
from application.orders.services.manage_repo import _create_order_with_items, _dto_to_order
from application.orders.services.manage_transformation import _transforming_order_creation_data
from application.orders.shemas.notification import OrderCreatedNotificationDTO


async def handle_order_created(
        unprocessed_notification: dict
):
    try:
        notification = OrderCreatedNotificationDTO.model_validate(unprocessed_notification)
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "ERROR_PARAMETER_VALUE_MISSED",
                    "message": "Parameter value missing.",
                    "details": str(e),
                }
            },
        )

    try:
        order_from_market = await get_order(notification.posting_number)
        orders_from_db = \
            await OrderRepository.get_order_items_by_posting_number(notification.posting_number)

        if len(orders_from_db) > 0:
            return JSONResponse(
                status_code=status.HTTP_409_CONFLICT,
                content={
                    "error": {
                        "code": "ERROR_REQUEST_DUPLICATED",
                        "message": "Order already exists.",
                        "details": None,
                    }
                },
            )

        order_items_dto = await _transforming_order_creation_data(
            notification=notification,
            order_data=order_from_market
        )

        dto_to_model = [_dto_to_order(dto) for dto in order_items_dto]
        print(order_items_dto, notification, order_from_market)

        orders = await _create_order_with_items(dto_to_model)

        if not orders:
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "ERROR_UNKNOWN",
                        "message": "Failed to write to the database.",
                        "details": None,
                    }
                },
            )

    except Exception as e:
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "ERROR_UNKNOWN",
                    "message": "Unknown error.",
                    "details": str(e),
                }
            },
        )

    return JSONResponse(status_code=200, content={"result": True})



