from fastapi import APIRouter, Body, status

from application.orders.services.use_case import handle_order_created

router = APIRouter(
    prefix="/webhook",
    tags=["webhook"]
)

@router.post("/notification")
async def notification(notification: dict = Body(...)):
    response = await handle_order_created(notification)
    return response






