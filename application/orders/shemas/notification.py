from datetime import datetime
from typing import List

from pydantic import BaseModel

from application.orders.shemas.enums import *

class NotificationTypeEnum(str, Enum):
    TYPE_NEW_POSTING = "TYPE_NEW_POSTING"   # Новое отправление.
    TYPE_POSTING_CANCELLED = "TYPE_POSTING_CANCELLED"   # Отмена отправления.
    TYPE_STATE_CHANGED = "TYPE_STATE_CHANGED"   # Изменение статуса отправления.
    TYPE_CUTOFF_DATE_CHANGED = "TYPE_CUTOFF_DATE_CHANGED"   # Изменение даты отгрузки отправления.
    TYPE_DELIVERY_DATE_CHANGED = "TYPE_DELIVERY_DATE_CHANGED"   # Изменение даты доставки отправления.

class BaseOrderNotificationDTO(BaseModel):
    message_type: NotificationTypeEnum
    posting_number: str     # Номер отправления.
    seller_id: int

class OrderCreatedItemsDTO(BaseModel):
    sku: int
    offer_id: int   # Идентификатор товара в системе продавца — артикул.
    quantity: int

class OrderCancelledItemsDTO(BaseModel):
    sku: int
    quantity: int

class OrderCreatedNotificationDTO(BaseOrderNotificationDTO):
    products: List[OrderCreatedItemsDTO]
    in_process_at: datetime
    shipment_date: datetime
    delivery_date_begin: datetime
    delivery_date_end: datetime

class OrderCancelledNotificationDTO(BaseOrderNotificationDTO):
    products: List[OrderCancelledItemsDTO]
    old_state: str
    new_state: str
    changed_state_date: datetime

class OrderUpdatedStatusEnum(str, Enum):
    posting_acceptance_in_progress = "posting_acceptance_in_progress"   # Идёт приёмка.
    posting_created = "posting_created"     # Создана.
    posting_awaiting_registration = "posting_awaiting_registration"     # Ожидает регистрации.
    posting_transferring_to_delivery = "posting_transferring_to_delivery"   # Передаётся в доставку.
    posting_in_carriage = "posting_in_carriage"     # В перевозке.
    posting_not_in_carriage = "posting_not_in_carriage"     # Не добавлен в перевозку.
    posting_in_arbitration = "posting_in_arbitration"       # Арбитраж.
    posting_in_client_arbitration = "posting_in_client_arbitration"     # Клиентский арбитраж.
    posting_on_way_to_city = "posting_on_way_to_city"       	# На пути в ваш город.
    posting_transferred_to_courier_service = "posting_transferred_to_courier_service"       # Передаётся курьеру.
    posting_in_courier_service = "posting_in_courier_service"       # Курьер в пути.
    posting_on_way_to_pickup_point = "posting_on_way_to_pickup_point"       # На пути в пункт выдачи.
    posting_in_pickup_point = "posting_in_pickup_point"     # В пункте выдачи.
    posting_conditionally_delivered = "posting_conditionally_delivered"     # Условно доставлено.
    posting_driver_pick_up = "posting_driver_pick_up"       # У водителя.
    posting_delivered = "posting_delivered"     # Доставлено.
    posting_received = "posting_received"       # Получено.
    posting_canceled = "posting_canceled"       # Отменено.
    posting_not_in_sort_center = "posting_not_in_sort_center"    # Не принято на сортировочном центре.

class OrderUpdatedStatusNotificationDTO(BaseOrderNotificationDTO):
    new_state: OrderUpdatedStatusEnum
    changed_state_date: datetime

class OrderUpdatedShipmentDateNotificationDTO(BaseOrderNotificationDTO):
    new_cutoff_date: datetime
    old_cutoff_date: datetime

class OrderUpdatedDeliveryDateNotificationDTO(BaseOrderNotificationDTO):
    new_delivery_date_begin: datetime
    new_delivery_date_end: datetime
    old_delivery_date_begin: datetime
    old_delivery_date_end: datetime

