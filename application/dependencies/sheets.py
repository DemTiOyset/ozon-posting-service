from application.config import settings
from application.orders.integrations.google_sheets.client import build_sheets_service
from application.orders.integrations.google_sheets.repository import SheetsRepository


def get_sheets_repo() -> SheetsRepository:
    service = build_sheets_service(settings.GOOGLE_SECRET_PATH)
    return SheetsRepository(
        service=service,
        spreadsheet_id=settings.GOOGLE_SHEET_ID,
        sheet_name=settings.GOOGLE_SHEET_NAME,
    )

