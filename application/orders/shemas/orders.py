from datetime import datetime
from http.client import responses
from typing import List, Optional

from pydantic import BaseModel, ConfigDict, Field, AliasChoices

from application.orders.shemas.enums import *

class OrderDTO(BaseModel):
    """CreateOrderDTO"""
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True)
    name: str | None = None
    posting_number: str | None = None
    seller_id: int | None = None
    commission_amount: float | None = None  # Размер комиссии за товар.
    commission_percent: int | None = None  # Процент комиссии.
    payout: float  # Выплата продавцу.
    price: float  # Цена товара с учётом акций, кроме акций за счёт Ozon.
    customer_price: float  # Цена товара для покупателя с учётом скидок продавца и Ozon.
    total_discount_percent: float  # Процент скидки.
    total_discount_value: float  # Сумма скидки.
    sku: int
    shipment_date: datetime | None = None
    delivery_date_begin: datetime | None = None
    delivery_date_end: datetime | None = None
    offer_id: str | None = None
    status: str | None = None
    last_event_time: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "in_process_at",
            "changed_state_date",
        ),
    )