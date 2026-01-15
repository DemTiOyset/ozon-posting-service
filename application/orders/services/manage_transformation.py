from typing import Iterable, List

from application.orders.shemas.notification import OrderCreatedNotificationDTO, \
    BaseOrderNotificationDTO, OrderCancelledNotificationDTO, OrderUpdatedStatusEnum, \
    OrderUpdatedShipmentDateNotificationDTO, OrderUpdatedStatusNotificationDTO, OrderUpdatedDeliveryDateNotificationDTO
from application.orders.shemas.orders_from_market import FinancialOrderDataDTO, ReceivedOrderDTO
from application.orders.shemas.orders import OrderDTO


async def _transforming_order_creation_data(
        notification: OrderCreatedNotificationDTO,
        order_data: ReceivedOrderDTO
) -> List[OrderDTO]:

    last_event_time = notification.in_process_at
    delivery_date_begin = notification.delivery_date_begin
    delivery_date_end = notification.delivery_date_end
    posting_number = notification.posting_number
    seller_id = notification.seller_id

    order_items: list[OrderDTO] = []
    for product in notification.products:
        sku = product.sku
        offer_id = product.offer_id
        quantity = product.quantity
        status = OrderUpdatedStatusEnum.posting_created.value

        for financial_data_product in order_data.financial_datas.products:
            if sku == financial_data_product.product_id:
                order_item = OrderDTO.model_validate({
                    "offer_id": offer_id,
                    "quantity": quantity,
                    "sku": sku,
                    "commission_amount": financial_data_product.commission_amount,
                    "commission_percent": financial_data_product.commission_percent,
                    "payout": financial_data_product.payout,
                    "price": financial_data_product.price,
                    "customer_price": financial_data_product.customer_price,
                    "total_discount_percent": financial_data_product.total_discount_percent,
                    "total_discount_value": financial_data_product.total_discount_value,
                    "last_event_time": last_event_time,
                    "delivery_date_begin": delivery_date_begin,
                    "delivery_date_end": delivery_date_end,
                    "posting_number": posting_number,
                    "seller_id": seller_id,
                    "status": status
                })
                order_items.append(order_item)

    return order_items


async def _transforming_order_cancellation_data(
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


async def _transforming_order_shipment_date_update(
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


async def _transforming_order_status_update(
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


async def _transforming_order_delivery_date_update(
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



