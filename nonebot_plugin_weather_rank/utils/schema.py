from nonebot import require
from sqlalchemy.orm import Mapped, mapped_column

require('nonebot_plugin_orm')
from nonebot_plugin_orm import Model  # noqa: E402


class Weather(Model):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    group_id: Mapped[int]
    location_code: Mapped[str]
    location_name: Mapped[str]
