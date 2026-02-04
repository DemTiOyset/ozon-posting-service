from fastapi import APIRouter, Body, status, Depends
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from application.clients.market.client import get_order
from application.database.db import get_db
from application.dependencies.sheets import get_sheets_repo
from application.repositories.google_sheets.repository import SheetsRepository
from application.services.use_case import handle_order_created, handle_order_updated_shipment_date
from application.sсhemas.notification import OrderCreatedNotificationDTO, NotificationTypeEnum, \
    OrderUpdatedShipmentDateNotificationDTO

from application.v1.responses import Responses

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/notification")
async def notification(
        unprocessed_notification: dict = Body(...),
        repo: SheetsRepository = Depends(get_sheets_repo),
        session: AsyncSession = Depends(get_db),
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
        order = await get_order(unprocessed_notification.get("posting_number"))
        if unprocessed_notification.get("message_type") == NotificationTypeEnum.TYPE_NEW_POSTING:
            processed_notification = OrderCreatedNotificationDTO.model_validate(unprocessed_notification)
            created_order_response = await handle_order_created(processed_notification, repo, session, order)
            response = Responses.responses(created_order_response)
            return response

        elif unprocessed_notification.get("message_type") == NotificationTypeEnum.TYPE_CUTOFF_DATE_CHANGED:
            processed_notification = OrderUpdatedShipmentDateNotificationDTO.model_validate(unprocessed_notification)
            response = await handle_order_updated_shipment_date(processed_notification, repo, session, order)
            if response.get("message") == "There is no such entry in the database":
                updated_shipment_date_response = await handle_order_created(processed_notification, repo, session, order)
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





