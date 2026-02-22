"""
    Это Use Case слой, который оркестрирует сценарии бизнес-логики проекта:
        1. Создание заказа
        2. Обновление заказа (статус, дата отгрузки, даты начала и конца заказа)
        3. Отмена заказа
    Данный слой независим от контрактов
"""
import logging

from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from application.clients.market.client import get_order
from application.repositories.google_sheets.repository import SheetsRepository
from application.repositories.repo import OrderRepository
from application.services.sheets import _create_order_items_in_sheets, _update_order_status, _update_ship_date
from application.sсhemas.transformation import dto_to_order, \
    transforming_order_items_creation, dto_to_order_items, transforming_order_data_creation_for_db, \
    transforming_order_data_creation_for_sheets
from application.sсhemas.notification import OrderCreatedNotificationDTO, OrderUpdatedShipmentDateNotificationDTO, \
    OrderUpdatedStatusNotificationDTO, OrderCancelledNotificationDTO, STATUS_LABELS

logger = logging.getLogger(__name__)


async def handle_order_created(
        notification: OrderCreatedNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession,
):
    """
    Обработчик создания заказа из вебхука маркетплейса.

    Args:
        notification: Данные из вебхука
        sheet_repo: Репозиторий для работы с Google Sheets
        session: Async SQLAlchemy session

    Returns:
        dict: Статус выполнения операции
    """
    posting_number = notification.posting_number

    # Логируем начало обработки
    logger.info(f"Processing order created webhook for posting: {posting_number}")

    try:
        # 1. Получить данные заказа из маркетплейса
        logger.debug(f"Fetching order data from marketplace: {posting_number}")
        order_from_market = await get_order(posting_number)

        # 2. Проверить существование в БД
        order_from_db = await OrderRepository.get_one_or_none_by_posting_number(
            session, posting_number
        )

        order_dto_for_db = transforming_order_data_creation_for_db(
            order_data=order_from_market
        )  # Преобразование данных полученных из get_order в pydantic схему, которую можно преобразовать в ORM модель

        order_dto_for_sheets = transforming_order_data_creation_for_sheets(
            order_data=order_from_market
        )

        order_items_dto = transforming_order_items_creation(
            order_data=order_from_market
        )

        logger.debug(
            f"Transformed order data: {len(order_items_dto)} items for posting {posting_number}"
        )

        if order_from_db is not None:
            logger.info(f"Order {posting_number} already exists in database, skipping creation")
        else:
            logger.info(f"Order {posting_number} not found, creating new record")

            # 4. Конвертация DTO → ORM модели
            dto_order_to_model = dto_to_order(order_dto_for_db)
            dto_items_to_model = [dto_to_order_items(dto) for dto in order_items_dto]

            # 5. Сохранение в БД
            logger.debug(f"Saving order {posting_number} to database")
            orders = await OrderRepository.create_order_with_items(session, dto_order_to_model, dto_items_to_model)   # Создание записи в бд
            await session.commit()

            logger.info(
                f"Successfully created order {posting_number} with {len(dto_items_to_model)} items"
            )

        # 6. Создание записи в Google Sheets
        logger.debug(f"Creating sheet entry for order {posting_number}")

        order_items_to_sheet = _create_order_items_in_sheets(sheet_repo, order_dto_for_sheets, order_items_dto)   # Создание записи о заказе в таблице

    except IntegrityError as e:
        # Конфликт уникальности (например, дублирующийся posting_number)
        logger.error(
            f"Integrity constraint violation for order {posting_number}: {e}",
            exc_info=True  # включает полный traceback
        )
        await session.rollback()
        return {"message": "Ok"}

    except SQLAlchemyError:
        await session.rollback()
        return {"message": "Order creation failed"}

    except Exception as e:  # Отлов ошибок
        return  {"message": "Unknown error", "error": str(e)}
        

    return {"message": "Ok"}
    


async def handle_order_updated_shipment_date(
        notification: OrderUpdatedShipmentDateNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession
):
    posting_number = notification.posting_number

    logger.info(f"Processing order update shipment date {notification.new_cutoff_date} webhook for posting: {posting_number}")

    try:
        order_from_db = \
            await OrderRepository.get_one_or_none_by_posting_number(session, posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if order_from_db is None:
            logger.info(f"Order {posting_number} does not exists in database, trying creation")
            return {"message": "There is no such entry in the database"}

        shipment_date_from_db = order_from_db.shipment_date

        if shipment_date_from_db == notification.new_cutoff_date:
            logger.info(f"The shipment date {shipment_date_from_db} in the database in order "
                        f"{posting_number} is the same as in the webhook {notification.new_cutoff_date}.")
            return {"message": "New cutoff date equal to the entry in the database"}

        logger.debug(f"Updating order {posting_number} shipment date in database")
        orders = await OrderRepository.update_order_shipment_date(session, posting_number, notification.new_cutoff_date)
        await session.commit()

        logger.debug(f"Successfully updated order {posting_number} shipment date {notification.new_cutoff_date} in database")
        
        if not orders:
            logger.info(f"Changes to the order {posting_number} regarding the shipping date were not saved.")
            return  {"message": "Order creation in database failed"}

        logger.debug(f"Updating order {posting_number} shipment date in sheet")

        update_order_shipment_date_in_sheets = _update_ship_date(sheet_repo, posting_number, notification.new_cutoff_date)

        logger.debug(f"Successfully updated order {posting_number} shipment date {notification.new_cutoff_date} in sheet")

    except SQLAlchemyError:
        await session.rollback()
        return {"message": "Order creation failed"}

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}
        
            
    return {"message": "Ok"}
    

async def handle_order_updated_status(
        notification: OrderUpdatedStatusNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession
):
    posting_number = notification.posting_number

    logger.info(
        f"Processing order update status {notification.new_state} webhook for posting: {posting_number}"
    )

    try:
        order_from_db = \
            await OrderRepository.get_one_or_none_by_posting_number(session, posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if order_from_db is None:
            logger.info(f"Order {posting_number} does not exists in database, trying creation")
            return {"message": "There is no such entry in the database"}

        last_event_time_from_db = order_from_db.last_event_time

        if last_event_time_from_db >= notification.changed_state_date:
            logger.info(f"The last event time {last_event_time_from_db} in the database in order "
                        f"{posting_number} is the same as in the webhook {notification.changed_state_date}.")
            return {"message": "The changed state date is less than the last change date in the database"}


        logger.debug(f"Updating order {posting_number} status in database")

        orders = await OrderRepository.update_order_status(session, posting_number, notification.new_state)
        await session.commit()

        logger.debug(
            f"Successfully updated order {posting_number} status {notification.new_state} in database")

        if not orders:
            logger.info(f"Changes to the order {posting_number} regarding the status were not saved.")
            return {"message": "Order creation in database failed"}

        logger.debug(f"Updating order {posting_number} status in sheet")

        update_order_status_in_sheets = _update_order_status(sheet_repo, posting_number, STATUS_LABELS.get(notification.new_state))

        logger.debug(
            f"Successfully updated order {posting_number} status {notification.new_state} in sheet")

    except SQLAlchemyError:
        await session.rollback()
        return {"message": "Order creation failed"}

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}
        

    return {"message": "Ok"}
    


async def handle_order_items_returned(
        notification: OrderCancelledNotificationDTO,
        sheet_repo: SheetsRepository,
        session: AsyncSession
):
    posting_number = notification.posting_number

    logger.info(f"Processing order items returning webhook for posting: {posting_number}")

    try:
        order_from_db = \
            await OrderRepository.get_one_or_none_by_posting_number(session, notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

        if order_from_db is None:
            logger.info(f"Order {posting_number} does not exists in database, trying creation")
            return {"message": "There is no such entry in the database"}

        for item in len(notification.products):
            less_quantity = await OrderRepository.reduce_item_quantity(session, posting_number, notification.products[item].sku, notification.products[item].quantity)
            establish_cancelled = await OrderRepository.establish_cancelled(session, posting_number, notification.products[item].sku)
        await session.commit()

    except ValueError as e:
        return {"message": "The quantity to be reduced is greater than the existing quantity.", "error": str(e)}

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}





