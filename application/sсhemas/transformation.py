from typing import List

from application.database.models.orders import Orders
from application.sсhemas.notification import OrderCancelledNotificationDTO, OrderUpdatedStatusEnum, \
    OrderUpdatedShipmentDateNotificationDTO, OrderUpdatedStatusNotificationDTO, OrderUpdatedDeliveryDateNotificationDTO
from application.sсhemas.orders_from_market import ReceivedOrderDTO
from application.sсhemas.orders import OrderDTO


async def transforming_order_data_creation(
        order_data: ReceivedOrderDTO
) -> List[OrderDTO]:

    last_event_time = order_data.in_process_at
    posting_number = order_data.posting_number
    shipment_date = order_data.shipment_date
    status = order_data.status

    order_items: List[OrderDTO] = []
    for product in order_data.products:
        sku = product.sku
        offer_id = product.offer_id
        quantity = product.quantity
        name = product.name

        for financial_data_product in order_data.financial_data.products:
            if sku == financial_data_product.product_id:
                order_item = OrderDTO.model_validate({
                    "name": name,
                    "offer_id": offer_id,
                    "quantity": quantity,
                    "sku": sku,
                    "shipment_date": shipment_date,
                    "commission_amount": financial_data_product.commission_amount,
                    "commission_percent": financial_data_product.commission_percent,
                    "payout": financial_data_product.payout,
                    "price": financial_data_product.price,
                    "customer_price": financial_data_product.customer_price,
                    "total_discount_percent": financial_data_product.total_discount_percent,
                    "total_discount_value": financial_data_product.total_discount_value,
                    "last_event_time": last_event_time,
                    "posting_number": posting_number,
                    "status": status
                })
                order_items.append(order_item)

    return order_items


async def transforming_order_cancellation_data(
        notification: OrderCancelledNotificationDTO
) -> List[OrderDTO]:

    last_event_time = notification.changed_state_date
    status = notification.new_state
    posting_number = notification.posting_number
    seller_id = notification.seller_id

    order_cancellation_items: list[OrderDTO] = []
    for product in notification.products:
        order_cancellation_item = OrderDTO.model_validate({
            "posting_number": posting_number,
            "seller_id": seller_id,
            "sku": product.sku,
            "status": status,
            "last_event_time": last_event_time,
            "quantity": product.quantity
        })

        order_cancellation_items.append(order_cancellation_item)

    return order_cancellation_items


async def transforming_order_shipment_date_update(
        notification: OrderUpdatedShipmentDateNotificationDTO,
) -> OrderDTO:
    new_shipment_date = notification.new_cutoff_date
    posting_number = notification.posting_number
    seller_id = notification.seller_id

    updated_shipment_date = OrderDTO.model_validate({
        "shipment_date": new_shipment_date,
        "posting_number": posting_number,
        "seller_id": seller_id,
    })

    return updated_shipment_date


async def transforming_order_status_update(
        notification: OrderUpdatedStatusNotificationDTO
) -> OrderDTO:
    last_event_time = notification.changed_state_date
    status = notification.new_state
    posting_number = notification.posting_number
    seller_id = notification.seller_id

    updated_order_status = OrderDTO.model_validate({
        "status": status,
        "last_event_time": last_event_time,
        "posting_number": posting_number,
        "seller_id": seller_id,
    })

    return updated_order_status


async def transforming_order_delivery_date_update(
    notification: OrderUpdatedDeliveryDateNotificationDTO,
) -> OrderDTO:
    new_delivery_date_begin = notification.new_delivery_date_begin
    new_delivery_date_end = notification.new_delivery_date_end
    posting_number = notification.posting_number
    seller_id = notification.seller_id

    updated_order_delivery_date = OrderDTO.model_validate({
        "delivery_date_begin": new_delivery_date_begin,
        "delivery_date_end": new_delivery_date_end,
        "posting_number": posting_number,
        "seller_id": seller_id,
    })

    return updated_order_delivery_date



def _dto_to_order(dto: OrderDTO) -> Orders:
    data = dto.model_dump(exclude_none=True)
    return Orders(**data)
