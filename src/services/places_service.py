import logging.config
from typing import Optional

from fastapi import Depends
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession

from clients.geo import LocationClient
from integrations.db.session import get_session
from integrations.events.producer import EventProducer
from integrations.events.schemas import CountryCityDTO
from models import Place
from repositories.places_repository import PlacesRepository
from schemas.places import PlaceUpdate
from settings import settings

logging.config.fileConfig("logging.conf")
logger = logging.getLogger()


class PlacesService:
    """
    Сервис для работы с информацией о любимых местах.
    """

    def __init__(self, session: AsyncSession = Depends(get_session)):
        """
        Инициализация сервиса.

        :param session: Объект сессии для взаимодействия с базой данных
        """

        self.session = session
        self.places_repository = PlacesRepository(session)

    async def get_places_list(self) -> list[Place]:
        """
        Получение списка любимых мест.
        :return:
        """

        return await self.places_repository.find_all_by()

    async def get_place(self, primary_key: int) -> Optional[Place]:
        """
        Получение объекта любимого места по его идентификатору.

        :param primary_key: Идентификатор объекта.
        :return:
        """

        return await self.places_repository.find(primary_key)

    @staticmethod
    def publish_event(place: Place):
        """
        Публикация ивента о попытке импорта информации из Country Informer Service.

        :param Place place: Место.
        :return:
        """
        try:
            place_data = CountryCityDTO(
                city=place.city if place.city else "",
                alpha2code=place.country,
            )
            EventProducer().publish(
                queue_name=settings.rabbitmq.queue.places_import, body=place_data.json()
            )
        except ValidationError:
            logger.warning(
                "The message was not well-formed during publishing event.",
                exc_info=True,
            )

    @staticmethod
    async def detailed_place(data: PlaceUpdate) -> Optional[Place]:
        """
        Получение деталей о месте.
        :param PlaceUpdate data: данные о месте
        :return:
        """
        if location := await LocationClient().get_location(latitude=data.latitude,
                                                         longitude=data.longitude):
            place = Place(
                latitude=location.latitude,
                longitude=location.longitude,
                description=data.description,
                country=location.alpha2code,
                city=location.city,
                locality=location.locality
            )
            return place
        return None

    async def create_place(self, data: PlaceUpdate) -> Optional[int]:
        """
        Создание нового объекта любимого места по переданным данным.

        :param data: Данные создаваемого объекта.
        :return: Идентификатор созданного объекта.
        """
        # Получение места с деталями
        place = await self.detailed_place(data)
        if place:
            primary_key = await self.places_repository.create_model(place)
            await self.session.commit()

            # публикация события о создании нового объекта любимого места
            # для попытки импорта информации по нему в сервисе Countries Informer
            self.publish_event(place)

            return primary_key
        return None

    async def update_place(self, primary_key: int, data: PlaceUpdate) -> Optional[int]:
        """
        Обновление объекта любимого места по переданным данным.

        :param primary_key: Идентификатор объекта.
        :param data: Данные для обновления объекта.
        :return:
        """
        if data.longitude or data.latitude:
            # Обновляем данные о месте при изменении координат
            place = await self.detailed_place(data)
        else:
            place = await self.get_place(primary_key)
            place.description = data.description
        matched_rows = await self.places_repository.update_model(
            primary_key, **place.dict(exclude_unset=True)
        )
        await self.session.commit()
        self.publish_event(place)
        return matched_rows

    async def delete_place(self, primary_key: int) -> Optional[int]:
        """
        Удаление объекта любимого места по его идентификатору.

        :param primary_key: Идентификатор объекта.
        :return:
        """

        matched_rows = await self.places_repository.delete_by(id=primary_key)
        await self.session.commit()

        return matched_rows
