from fastapi import APIRouter, Request, Body
from starlette.responses import JSONResponse
from typing import Any
from pydantic import ValidationError

from router.enums import *
from router.message_schemas import *
from router.param_shemas import *


router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/notification")
async def notification(request: Request, payload: dict[str, Any] = Body(example={"example": "value"})):
    try:
        base = BaseDTO.model_validate(payload)

    except Exception:
        er = NotificationApiErrorDTO(
            message="Неверный тип уведомления.",
            type=NotificationApiErrorType.WRONG_EVENT_FORMAT,
            status_code=400
            )
        return JSONResponse(status_code=400, content=er.model_dump())

    try:
        if base.notificationType == NotificationType.ORDER_CREATED:
            return await order_created_handler(payload)

    except Exception as e:
        raise e


async def order_created_handler(payload: dict[str, Any]):
    try:
        message = OrderCreatedNotificationDTO.model_validate(payload)
    except ValidationError as e:
        er = NotificationApiErrorDTO(
            message="Неверный тип уведомления ORDER_CREATED.",
            type=NotificationApiErrorType.WRONG_EVENT_FORMAT,
            status_code=400
        )
        return JSONResponse(status_code=400, content=er.model_dump())

    return message







