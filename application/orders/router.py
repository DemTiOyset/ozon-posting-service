from fastapi import APIRouter, Body, status, Depends
from pydantic import ValidationError
from fastapi.responses import JSONResponse

from application.dependencies.sheets import get_sheets_repo
from application.orders.integrations.google_sheets.repository import SheetsRepository
from application.orders.services.use_case import handle_order_created
from application.orders.shemas.notification import OrderCreatedNotificationDTO, NotificationTypeEnum

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/notification")
async def notification(
        unprocessed_notification: dict = Body(...),
        repo: SheetsRepository = Depends(get_sheets_repo)
):
    if unprocessed_notification.get("message_type") == NotificationTypeEnum.TYPE_PING:
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
               "version": "1.0.0",
               "name": "Gorbushka Keepers Ozon",
               "time": unprocessed_notification.get("time")
            }
        )

    try:
        notification = OrderCreatedNotificationDTO.model_validate(unprocessed_notification)
    except ValidationError as e:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={
                "error": {
                    "code": "ERROR_PARAMETER_VALUE_MISSED",
                    "message": "Пропущен необходимый параметр",
                    "details": str(e),
                }
            },
        )

    response = await handle_order_created(notification, repo)

    if response.get("message") == "Order creation failed":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "ERROR_PARAMETER_VALUE_MISSED",
                    "message": "Ошибка при записи в базу данных.",
                    "details": None,
                }
            },
        )

    elif response.get("message") == "Order creation in sheet failed":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "ERROR_UNKNOWN",
                    "message": "Ошибка записи в таблицу для отчетности.",
                    "details": None,
                }
            },
        )
    elif response.get("message") == "Неизвестная ошибка":
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "error": {
                    "code": "ERROR_UNKNOWN",
                    "message": "Unknown error.",
                    "details": response.get("error"),
                }
            },
        )
    elif response.get("message") == "Ok":
        return JSONResponse(status_code=200, content={"result": True})

    return JSONResponse(status_code=200, content={"result": True})






