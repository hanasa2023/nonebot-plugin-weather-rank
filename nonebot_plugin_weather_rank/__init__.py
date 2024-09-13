from nonebot.plugin import PluginMetadata

from .config import Config
from .utils.schema import Weather  # noqa: F401
from .weather_rank import weather_rank, weather_rank_helper  # noqa: F401

__version__ = '0.1.1'
__plugin_meta__ = PluginMetadata(
    name='weather-rank',
    description='订阅地区的天气排行榜',
    usage='获取气温/昼夜温差排行榜、获取气温图、当地天气',
    type='application',
    homepage='https://github.com/hanasa2023/nonebot-plugin-weather-rank#readme',
    config=Config,
    supported_adapters={'~onebot.v11'},
    extra={
        'version': __version__,
        'authors': [
            'hanasaki <hanasakayui2022@gmail.com>',
        ],
    },
)
