from nonebot import get_driver, get_plugin_config
from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""

    qweather_api_key: str = ''


plugin_config: Config = get_plugin_config(Config)

DRIVER = get_driver()

config = DRIVER.config

SUPERUSERS: set[str] = config.superusers
