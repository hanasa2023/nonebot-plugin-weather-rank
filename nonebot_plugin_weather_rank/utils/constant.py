from ..config import plugin_config


NOW_WEATHER_SEARCH_BASE_URL = (
    'https://devapi.qweather.com/v7/weather/now?'
    if plugin_config.qweather_rank_mode == 0
    else 'https://api.qweather.com/v7/weather/now?'
)
DAILY_WEATHER_SEARCH_BASE_URL = (
    'https://devapi.qweather.com/v7/weather/7d?'
    if plugin_config.qweather_rank_mode == 0
    else 'https://api.qweather.com/v7/weather/7d?'
)
HOURLY_WEATHER_SEARCH_BASE_URL = (
    'https://devapi.qweather.com/v7/weather/24h?'
    if plugin_config.qweather_rank_mode == 0
    else 'https://api.qweather.com/v7/weather/24h?'
)
AIR_QUALITY_BASE_URL = (
    'https://devapi.qweather.com/v7/air/now?'
    if plugin_config.qweather_rank_mode == 0
    else 'https://api.qweather.com/v7/air/now?'
)
CITY_SEARCH_BASE_URL = 'https://geoapi.qweather.com/v2/city/lookup?'
TEMPERATURE_MAP_BASE_URL = (
    'http://www.nmc.cn/publish/observations/hourly-temperature.html'
)
