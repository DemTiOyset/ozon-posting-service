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
    product_id: int     # sku.


class FinancialOrderDataDTO(BaseModel):
    products: List[ProductFinancialOrderDTO]

class ProductOrderDTO(BaseModel):
    name: str
    quantity: str
    sku: int


class ReceivedOrderDTO(BaseModel):
    posting_number: int
    status: str
    in_process_at: datetime     # Дата и время начала обработки отправления.
    products: List[ProductOrderDTO]
    financial_datas: Optional[FinancialOrderDataDTO]


class ReceivedBusinessOrderDTO(BaseModel):
    result: ReceivedOrderDTO



