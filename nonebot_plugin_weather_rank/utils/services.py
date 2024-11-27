from __future__ import annotations

from typing import cast

from loguru import logger
from nonebot import require
from pydantic import BaseModel
from tortoise import Tortoise
from tortoise.transactions import in_transaction

from .schema import Weather, WeatherSubscribed

require('nonebot_plugin_localstore')
from nonebot_plugin_localstore import get_plugin_data_file  # noqa: E402


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
        self.initalized = False

    async def init(self):
        if not self.initalized:
            self.initalized = True
            await Tortoise.init(
                {
                    'connections': {
                        'default': {
                            'engine': 'tortoise.backends.sqlite',
                            'credentials': {
                                'file_path': str(get_plugin_data_file('weather.db'))
                            },
                        }
                    },
                    'apps': {
                        'events': {
                            'models': ['nonebot_plugin_weather_rank.utils.schema'],
                            'default_connection': 'default',
                        }
                    },
                }
            )
            await Tortoise.generate_schemas()

    async def add_location_for_group(
        self, group_id: int, location_code: str, location_name: str
    ) -> str:
        """向群组中添加订阅地区

        Args:
            group_id (int): 群组id
            location_code (str): 地区代码
            location_name (str): 地区名

        Returns:
            str: 添加成功/失败信息
        """
        async with in_transaction() as _:
            w = await Weather.filter(group_id=group_id, location_code=location_code)
            if len(w) != 0:
                return f'该城市/地区{location_name}已存在'
            else:
                await Weather.create(
                    group_id=group_id,
                    location_code=location_code,
                    location_name=location_name,
                )
                return f'添加{location_name}成功'

    async def get_locations_in_group(self, group_id: int) -> list[LocationInfo]:
        """获取群组内订阅的地区信息

        Args:
            group_id (int): 群组id

        Returns:
            tuple[list[str], list[str]]: 地区和地区名称列表
        """
        async with in_transaction() as _:
            weathers = await Weather.filter(group_id=group_id)
            locations: list[LocationInfo] = []
            for weather in weathers:
                locations.append(
                    LocationInfo(code=weather.location_code, name=weather.location_name)
                )

            return locations

    async def remove_location_from_group(
        self, group_id: int, location_code: str
    ) -> str:
        """从群组中删除城市

        Args:
            group_id (int): 群组id
            location_code (str): 地区代码

        Returns:
            str: _description_
        """
        async with in_transaction() as _:
            logger.debug(f'group id is {group_id}, location is {location_code}')
            location = await Weather.filter(
                group_id=group_id, location_code=location_code
            )

            logger.info(f'location : {location}')
            for loc in location:
                await Weather.delete(loc)
            return f'删除{location[0].location_name}成功'

    async def get_subscribed_groups(self) -> list[int]:
        """获取已订阅的群组

        Returns:
            List[str]: 群组id列表
        """
        async with in_transaction() as _:
            groups: list[WeatherSubscribed] = await WeatherSubscribed.all()
            return [group.group_id for group in groups]

    async def add_subscribed_group(self, group_id: int) -> str:
        """添加订阅群组

        Args:
            group_id (str): 群组id

        Returns:
            str: 订阅成功信息
        """
        try:
            async with in_transaction() as _:
                await WeatherSubscribed.create(group_id=group_id)
                return '订阅成功'
        except Exception as _:
            return '已经订阅过了'

    async def remove_subscribed_group(self, group_id: int) -> str:
        """移除订阅群组

        Args:
            group_id (str): 群组id

        Returns:
            str: 移除成功信息
        """
        async with in_transaction() as _:
            group: list[WeatherSubscribed] = await WeatherSubscribed.filter(
                group_id=group_id
            )
            if len(group) == 0:
                return f'群组{group_id}未订阅'
            else:
                await WeatherSubscribed.delete(group[0])
                return '取消订阅成功'

    @classmethod
    def get_instance(cls) -> 'DBService':
        """获取Weather单例

        Returns:
            Self: Weather实例
        """
        if cls._instance is None:
            cls._instance = cls()
        return cast('DBService', cls._instance)
