"""
    Это Use Case слой, который оркестрирует сценарии бизнес-логики проекта:
        1. Создание заказа
        2. Обновление заказа (статус, дата отгрузки, даты начала и конца заказа)
        3. Отмена заказа
    Данный слой независим от контрактов
"""
from application.database.db import async_session_maker
from application.repositories.google_sheets.repository import SheetsRepository
from application.clients.market.client import get_order
from application.repositories.repo import OrderRepository
from application.services.sheets import _create_order_items_in_sheets
from application.sсhemas.transformation import transforming_order_data_creation, _dto_to_order
from application.sсhemas.notification import OrderCreatedNotificationDTO, OrderUpdatedShipmentDateNotificationDTO, \
    OrderUpdatedStatusNotificationDTO


async def handle_order_created(
        notification: OrderCreatedNotificationDTO,
        repo: SheetsRepository,
):
    try:
        order_from_market = await get_order(notification.posting_number)    # Получение заказа с озона по его номеру из вебхука
        with async_session_maker as session:
            async with session.begin():
                repo = OrderRepository(session)
                orders_from_db = \
                    await repo.get_order_items_by_posting_number(notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука

                if len(orders_from_db) == 0:    # Проверка на наличие записи о заказе в бд, если записей нет, то программа записывает
                    order_items_dto = await transforming_order_data_creation(
                        order_data=order_from_market
                    )   # Преобразование данных полученных из get_order в pydantic схему, которую можно преобразовать в ORM модель

                    dto_to_model = [_dto_to_order(dto) for dto in order_items_dto]  # Преобразование pydantic схемы в ORM модель


                    orders = await repo.create_order_with_items(dto_to_model)   # Создание записи в бд

                    if not orders:  # Проверка того созданы ли записи в бд
                        return {"message": "Order creation in database failed"}
                

        order_items_to_sheet = await _create_order_items_in_sheets(repo, order_items_dto)   # Создание записи о заказе в таблице

        if not order_items_to_sheet:    # Проверка наличия записи в таблице
            return {"message": "Order creation in sheet failed"}
            

    except Exception as e:  # Отлов ошибок
        return  {"message": "Unknown error", "error": str(e)}
        

    return {"message": "Ok"}
    


async def handle_order_updated_shipment_date(
        notification: OrderUpdatedShipmentDateNotificationDTO,
        repo: SheetsRepository,
):
    try:
        order_from_market = await get_order(notification.posting_number)    # Получение заказа с озона по его номеру из вебхука
        with async_session_maker as session:
            async with session.begin():
                repo = OrderRepository(session)
                orders_from_db = \
                    await repo.get_order_items_by_posting_number(notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука
        
                if order_from_market == 0:
                    return {"message": "There is no such entry in the database"}
        
                order = await repo.get_first_order_by_posting_number(notification.posting_number)
        
                shipment_date_from_db = order.shipment_date
        
                if shipment_date_from_db == notification.new_cutoff_date:
                    return {"message": "New cutoff date equal to the entry in the database"}
                    
        
                orders = await repo.update_order_shipment_date(notification.posting_number, notification.new_cutoff_date)
        
        if not orders:
            return  {"message": "Order creation in database failed"}
            
        
        # Написать обновление в таблицах

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}
        
            
    return {"message": "Ok"}
    

async def handle_order_updated_status(
        notification: OrderUpdatedStatusNotificationDTO,
):
    try:
        order_from_market = await get_order(notification.posting_number)    # Получение заказа с озона по его номеру из вебхука
        with async_session_maker as session:
            async with session.begin():
                repo = OrderRepository(session)
                orders_from_db = \
                    await repo.get_order_items_by_posting_number(notification.posting_number)    # Получение записи заказа из бд по его номеру из вебхука
        
                if order_from_market == 0:
                    return {"message": "There is no such entry in the database"}
        
                order = await repo.get_first_order_by_posting_number(notification.posting_number)
        
                last_event_time_from_db = order.last_event_time
        
                if last_event_time_from_db >= notification.changed_state_date:
                    return {"message": "The changed state date is less than the last change date in the database"}
                    
        
                orders = await repo.update_order_status(notification.posting_number, notification.new_state)

        if not orders:
            return {"message": "Order creation in database failed"}
            

        # Написать обновление в таблицах

    except Exception as e:  # Отлов ошибок
        return {"message": "Unknown error", "error": str(e)}
        

    return {"message": "Ok"}
    








