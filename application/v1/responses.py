from fastapi.responses import JSONResponse
from fastapi import status


class Responses:
    @staticmethod
    def responses(handler_response: dict, details: str = None) -> JSONResponse:
        if handler_response.get("message") == "Order creation failed":
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "ERROR_PARAMETER_VALUE_MISSED",
                        "message": "Ошибка при записи в базу данных.",
                        "details": None,
                    }
                },
            )

        elif handler_response.get("message") == "Order creation in sheet failed":
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "ERROR_UNKNOWN",
                        "message": "Ошибка записи в таблицу для отчетности.",
                        "details": None,
                    }
                },
            )

        elif handler_response.get("message") == "Unknown error":
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "ERROR_UNKNOWN",
                        "message": "Неизвестная ошибка.",
                        "details": handler_response.get("error"),
                    }
                },
            )

        elif handler_response.get("message") == "New cutoff date equal to the entry in the database":
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "ERROR_REQUEST_DUPLICATED",
                        "message": "Дата в сервисе равна обновленной дате в уведомлении.",
                        "details": handler_response.get("error"),
                    }
                },
            )

        elif handler_response.get("message") == "New status entry equal to the entry in the database":
            return JSONResponse(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                content={
                    "error": {
                        "code": "ERROR_REQUEST_DUPLICATED",
                        "message": "Статус в сервисе равен обновленному статусу в уведомлении.",
                        "details": handler_response.get("error"),
                    }
                },
            )

        elif handler_response.get("message") == "Ok":
            return JSONResponse(status_code=200, content={"result": True})

        return JSONResponse(status_code=200, content={"result": True})