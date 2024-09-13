from __future__ import annotations

from typing import cast

from loguru import logger
from nonebot import require
from pydantic import BaseModel
from sqlalchemy import Select, select

from .schema import Weather

require('nonebot_plugin_orm')
from nonebot_plugin_orm import get_session  # noqa: E402


class LocationInfo(BaseModel):
    code: str
    name: str


class DBService:
    _instance: 'DBService | None' = None

    def __new__(cls, *args, **kwargs) -> 'DBService':
        if cls._instance is None:
            cls._instance = super(DBService, cls).__new__(cls, *args, **kwargs)
        return cast('DBService', cls._instance)

    def __init__(self) -> None:
        if not hasattr(self, 'session'):
            self.session = get_session()

    async def add_location_for_group(
        self, group_id: int, location_code: str, location_name: str
    ) -> str:
        """获取群组订阅的地区

        Args:
            group_id (int): 群组id
            location_code (str): 地区代码
            location_name (str): 地区名

        Returns:
            str: 添加成功/失败信息
        """
        w: Select[tuple[Weather]] = select(Weather).where(
            Weather.group_id.is_(group_id), Weather.location_code.is_(location_code)
        )
        wea: Weather | None = await self.session.scalar(w)
        if wea:
            return f'该城市/地区{wea.location_name}已存在'
        else:
            async with self.session as session:
                weather = Weather(
                    group_id=group_id,
                    location_code=location_code,
                    location_name=location_name,
                )

                session.add(weather)
                await session.commit()
                await session.refresh(weather)

                return f'添加{location_name}成功'

    async def get_locations_in_group(self, group_id: int) -> list[LocationInfo]:
        """获取群组内订阅的地区信息

        Args:
            group_id (int): 群组id

        Returns:
            tuple[list[str], list[str]]: 地区和地区名称列表
        """
        weathers = select(Weather).where(Weather.group_id.is_(group_id))
        locations: list[LocationInfo] = []
        for weather in await self.session.scalars(weathers):
            locations.append(
                LocationInfo(
                    code=weather.location_code,
                    name=weather.location_name,
                )
            )
        return locations

    async def remove_location_from_group(
        self, group_id: int, location_code: str
    ) -> None:
        async with self.session as session:
            location: Select[tuple[Weather]] = select(Weather).where(
                Weather.group_id.is_(group_id), Weather.location_code.is_(location_code)
            )
            logger.info(f'location : {location}')
            for loc in await session.scalars(location):
                await session.delete(loc)
            await session.commit()

    @classmethod
    def get_instance(cls) -> 'DBService':
        """获取Weather单例

        Returns:
            Self: Weather实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cast('DBService', cls._instance)
