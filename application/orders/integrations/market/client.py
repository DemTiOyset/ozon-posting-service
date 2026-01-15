import asyncio
from decimal import Decimal
from typing import List, Iterable

import httpx
import requests


from application.config import settings
from application.orders.shemas.orders_from_market import GetBusinessOrdersResponseDTO


from application.orders.test_json import a as test_json


async def get_order(
        campaign_id: int,
        order_id: int,
        url: str = f"https://"
                   f"api.partner.market.yandex.ru/v1/businesses/"
                   f"{settings.business_id}/orders",
):
    body = {
        "campaignIds": [campaign_id],
        "orderIds": [order_id]
        }

    headers = {
         "Api-Key": settings.api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    parsed = GetBusinessOrdersResponseDTO.model_validate(payload)

    order_data = parsed.orders[0]

    return order_data

async def get_prices_from_market(
        offer_ids: Iterable[str],
        url: str = f"https://"
                   f"api.partner.market.yandex.ru/v2/businesses/"
                   f"{settings.business_id}/offer-prices"
):

    body = {"offerIds": offer_ids}

    headers = {
        "Api-Key": settings.api_key,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    # payload["result"]["offers"] = [{ "offerId": "...", "price": {"value": ...}}, ...]
    offers = payload.get("result", {}).get("offers", [])

    prices_by_offer: dict[str, Decimal] = {}
    for offer in offers:
        oid = offer.get("offerId")
        price = (offer.get("price") or {}).get("value")
        if oid is None or price is None:
            continue
        prices_by_offer[oid] = Decimal(str(price))

    return prices_by_offer


