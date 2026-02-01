from fastapi import APIRouter, Body, status, Depends
from pydantic import ValidationError
from fastapi.responses import JSONResponse

from application.dependencies.sheets import get_sheets_repo
from application.orders.integrations.google_sheets.repository import SheetsRepository
from application.orders.services.use_case import handle_order_created, handle_order_updated_shipment_date
from application.orders.shemas.notification import OrderCreatedNotificationDTO, NotificationTypeEnum, \
    OrderUpdatedShipmentDateNotificationDTO

from application.v1.responses import Responses

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

        if unprocessed_notification.get("message_type") == NotificationTypeEnum.TYPE_NEW_POSTING:
            notification = OrderCreatedNotificationDTO.model_validate(unprocessed_notification)
            created_order_response = await handle_order_created(notification, repo)
            response = Responses.responses(created_order_response)
            return response

        elif unprocessed_notification.get("message_type") == NotificationTypeEnum.TYPE_CUTOFF_DATE_CHANGED:
            notification = OrderUpdatedShipmentDateNotificationDTO.model_validate(unprocessed_notification)
            response = await handle_order_updated_shipment_date(notification, repo)
            if response.get("message") == "There is no such entry in the database":
                updated_shipment_date_response = await handle_order_created(notification, repo)
                response = Responses.responses(updated_shipment_date_response)
                return response

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

    return JSONResponse(status_code=200, content={"result": True})





