import httpx

from application.config import settings
from application.sсhemas.orders_from_market import ReceivedBusinessOrderDTO


async def get_order(
        posting_number: str,
        url: str = "https://api-seller.ozon.ru/v3/posting/fbs/get"
):
    body = {
      "posting_number": posting_number,
      "with": {
        "financial_data": True
      }
    }

    headers = {
        "Client-ID": settings.CLIENT_ID,
        "Api-Key": settings.API_KEY,
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=20.0) as client:
        resp = await client.post(url, headers=headers, json=body)
        resp.raise_for_status()
        payload = resp.json()

    parsed = ReceivedBusinessOrderDTO.model_validate(payload)

    order_data = parsed.result

    return order_data



