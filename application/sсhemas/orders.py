from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, AliasChoices


class OrderDTO(BaseModel):
    """CreateOrderDTO"""
    model_config = ConfigDict(use_enum_values=True, populate_by_name=True, from_attributes=True)
    name: str | None = None
    posting_number: str | None = None
    quantity: int | None = None
    commission_amount: float | None = None  # Размер комиссии за товар.
    commission_percent: int | None = None  # Процент комиссии.
    payout: float  # Выплата продавцу.
    price: float  # Цена товара с учётом акций, кроме акций за счёт Ozon.
    customer_price: float  # Цена товара для покупателя с учётом скидок продавца и Ozon.
    total_discount_percent: float  # Процент скидки.
    total_discount_value: float  # Сумма скидки.
    sku: int
    shipment_date: datetime | None = None
    offer_id: str | None = None
    status: str | None = None
    last_event_time: datetime | None = Field(
        default=None,
        validation_alias=AliasChoices(
            "in_process_at",
            "changed_state_date",
        ),
    )

