from datetime import datetime
from typing import List

from application.repositories.google_sheets.columns import C
from application.repositories.google_sheets.repository import SheetsRepository
from application.sсhemas.orders import OrderDTO, OrderItemsDTO


def _create_order_items_in_sheets(
        repo: SheetsRepository,
        order: OrderDTO,
        order_items: List[OrderItemsDTO],
):
    columns: list[dict] = []
    for item in order_items:
        values = {
            C.key: make_key(order.posting_number, item.sku),
            C.row_type: "ITEM",
            C.ship_date: order.shipment_date.date().isoformat(),
            C.order_number: order.posting_number,
            C.qty: item.quantity,
            C.payout: item.payout,
            C.commission: item.commission_amount,
            C.ship_date_iso: order.shipment_date.date().isoformat(),
            C.name: item.name,
            C.buyer_price: item.customer_price,
            C.status: order.status,

        }
        column = repo.upsert_item(values=values)
        columns.append(column)

    return columns

def _update_order_status(
        repo: SheetsRepository,
        posting_number: str,
        status: str
):
    values = {
        C.row_type: "ITEM",
        C.status: status,
    }

    column = repo.update_by_posting_number(posting_number, values)
    return column

def _update_ship_date(
        repo: SheetsRepository,
        posting_number: str,
        new_ship_date: datetime
):
    new_ship_date_iso = new_ship_date.isoformat()
    column = repo.update_order_shipment_date_simple(posting_number, new_ship_date_iso)
    return column

def make_key(posting_number: str, sku_or_offer_id: int) -> str:
     return f"item:{posting_number}:{sku_or_offer_id}"





