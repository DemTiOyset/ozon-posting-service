from typing import List

from application.repositories.google_sheets.columns import C
from application.sсhemas.orders import OrderDTO


async def _create_order_items_in_sheets(
        repo,
        order_items: List[OrderDTO]
):
    columns: list[dict] = []
    for item in order_items:
        values = {
            C.key: make_key(item.posting_number, item.sku),
            C.row_type: "ITEM",
            C.ship_date: item.shipment_date.date().isoformat(),
            C.order_number: item.posting_number,
            C.qty: item.quantity,
            C.payout: item.payout,
            C.commission: item.commission_amount,
            C.ship_date_iso: item.shipment_date.date().isoformat(),
            C.name: item.name,
            C.buyer_price: item.customer_price,
            C.status: item.status,

        }
        column = repo.upsert_item(values=values)
        columns.append(column)

    return columns


def make_key(posting_number: str, sku_or_offer_id: str | int) -> str:
     return f"item:{posting_number}:{sku_or_offer_id}"



