from fastapi import FastAPI

from application.orders.router import router as webhook_router

app = FastAPI(
    title="Gorbushka Keepers Ozon",
    version="1.0.0",
)

app.include_router(webhook_router)


@app.get("/health")
async def health():
    return {"status": "ok"}