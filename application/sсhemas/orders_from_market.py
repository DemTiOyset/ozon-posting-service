from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel


class ProductFinancialOrderDTO(BaseModel):
    commission_amount: float    # Размер комиссии за товар.
    commission_percent: int     # Процент комиссии.
    payout: float   # Выплата продавцу.
    price: float    # Цена товара с учётом акций, кроме акций за счёт Ozon.
    customer_price: float    # Цена товара для покупателя с учётом скидок продавца и Ozon.
    total_discount_percent: float    # Процент скидки.
    total_discount_value: float      # Сумма скидки.
    product_id: int


class FinancialOrderDataDTO(BaseModel):
    products: List[ProductFinancialOrderDTO]

class ProductOrderDTO(BaseModel):
    name: str
    quantity: int
    sku: int
    offer_id: str

class ReceivedOrderDTO(BaseModel):
    posting_number: str
    status: str
    in_process_at: datetime     # Дата и время начала обработки отправления.
    shipment_date: datetime
    products: List[ProductOrderDTO]
    financial_data: FinancialOrderDataDTO | None = None



class ReceivedBusinessOrderDTO(BaseModel):
    result: ReceivedOrderDTO



