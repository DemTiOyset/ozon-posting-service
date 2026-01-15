# import requests
#
#
# from config import settings
#
# def get_orders(
#         headers: dict,
#         url: str,
#         date=1,
#         count=0
# ):
#     for i in range(30):
#         date_form = f"0{date}" if date < 10 else f"{date}"
#         params = {
#             "campaignIds": [settings.campaignId],
#             "dates": {
#                 "creationDateFrom": f"2025-12-{date_form}",
#                 "creationDateTo": f"2025-12-{date_form}",
#             },
#         }
#
#         response = requests.post(url, headers=headers, json=params)
#
#         if response.status_code == 200:
#             orders = response.json()
#             count += len(orders["orders"])
#         else:
#             print("Ошибка:", response.status_code)
#             print(response.text)
#             return None
#         date += 1
#     return count
#
# if __name__ == "__main__":
#     get_orders(
#         settings.headers,
#         settings.urls["get_orders"].format(businessId=settings.businessId)
#     )


from fastapi import FastAPI
from api.yandex_webhook import router as yandex_webhook

app = FastAPI(
    title="Gorbushka Keepers",
    debug=True,
)

app.include_router(yandex_webhook)


@app.get("/")
async def main():
    return {"message": "Hello World"}