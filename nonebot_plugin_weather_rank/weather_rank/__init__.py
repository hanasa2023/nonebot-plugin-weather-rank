from __future__ import annotations

from datetime import datetime
from pathlib import Path
from typing import Any

import httpx
from bs4 import BeautifulSoup, Tag
from nonebot import logger, require
from nonebot.adapters import Event

from ..config import plugin_config
from ..utils.addition_for_htmlrender import md_to_pic, template_element_to_pic
from ..utils.constant import (
    AIR_QUALITY_BASE_URL,
    CITY_SEARCH_BASE_URL,
    DAILY_WEATHER_SEARCH_BASE_URL,
    HOURLY_WEATHER_SEARCH_BASE_URL,
    NOW_WEATHER_SEARCH_BASE_URL,
    TEMPERATURE_MAP_BASE_URL,
)
from ..utils.model import (
    DailyWeather,
    FutureDailyWeatherItem,
    FutureHourlyWeatherItem,
    HourlyWeather,
    NowWeather,
    WeatherCardData,
    WeatherData,
)
from ..utils.services import DBService, LocationInfo

require('nonebot_plugin_alconna')
from nonebot_plugin_alconna import (  # noqa: E402
    Alconna,
    AlconnaMatcher,
    Args,
    Arparma,
    Field,
    Image,
    Subcommand,
    Target,
    UniMessage,
    on_alconna,
)

require('nonebot_plugin_apscheduler')
from nonebot_plugin_apscheduler import scheduler  # noqa: E402

weather_rank_commands: Alconna[Any] = Alconna(
    '天气',
    Subcommand(
        '排行榜',
        Args['mode', str, Field(completion=lambda: '请输入要生成的排行榜(气温/温差)')],
    ),
    Subcommand(
        '添加城市',
        Args['city', str, Field(completion=lambda: '请输入要添加的城市名称')],
    ),
    Subcommand(
        '删除城市',
        Args['city', str, Field(completion=lambda: '请输入要删除城市的名称')],
    ),
    Subcommand('气温地图'),
    Subcommand(
        '当地天气',
        Args['city', str, Field(completion=lambda: '请输入要查询的城市名称')],
    ),
    Subcommand('订阅'),
    Subcommand('取消订阅'),
)

weather_rank: type[AlconnaMatcher] = on_alconna(
    command=weather_rank_commands,
    aliases={'weather'},
    use_cmd_start=True,
    comp_config={'lite': True},
    skip_for_unmatch=False,
)


helper: Alconna[Any] = Alconna('天气帮助')
weather_rank_helper: type[AlconnaMatcher] = on_alconna(
    command=helper, aliases={'weather_rank_helper'}, use_cmd_start=True
)


@scheduler.scheduled_job(
    'cron',
    hour=plugin_config.schedule_hour,
    minute=plugin_config.schedule_minute,
    id='send_weather_info',
)
async def _() -> None:
    dbs: DBService = DBService.get_instance()
    await dbs.init()

    group_ids: list[int] = await dbs.get_subscribed_groups()

    for id in group_ids:
        target: Target = Target(str(id))

        if plugin_config.schedule_switch:
            logger.info('开始推送天气')
            locations: list[LocationInfo] = await dbs.get_locations_in_group(int(id))
            weathers: list[WeatherData] = []
            modes: list[str] = ['气温', '温差']
            for mode in modes:
                for location in locations:
                    async with httpx.AsyncClient() as ctx:
                        response: httpx.Response = await ctx.get(
                            f'{NOW_WEATHER_SEARCH_BASE_URL}location={location.code}&key={plugin_config.qweather_api_key}'
                            if mode == '气温'
                            else f'{DAILY_WEATHER_SEARCH_BASE_URL}location={location.code}&key={plugin_config.qweather_api_key}'
                        )
                        if response.status_code == 200:
                            if mode == '气温':
                                now_weather: NowWeather = NowWeather(**response.json())
                                weathers.append(
                                    WeatherData(
                                        name=location.name, temp=now_weather.now.temp
                                    )
                                )
                            elif mode == '温差':
                                daily_weather: DailyWeather = DailyWeather(
                                    **response.json()
                                )
                                weathers.append(
                                    WeatherData(
                                        name=location.name,
                                        temp=str(
                                            int(daily_weather.daily[0].temp_max)
                                            - int(daily_weather.daily[0].temp_min)
                                        ),
                                    )
                                )
                        else:
                            await UniMessage.text(
                                f'获取{location.name}天气信息失败'
                            ).send(target)
                # 对各地气温/温差进行排序
                weathers.sort(key=lambda x: int(x.temp), reverse=True)

                # 绘制排行榜
                template_path: str = str(Path(__file__).parent / 'templates')
                template_name: str = 'rank_card.html.jinja2'

                rank_img: bytes = await template_element_to_pic(
                    template_path,
                    template_name,
                    templates={'datas': weathers, 'mode': mode},
                    element='.container',
                    wait=2,
                    omit_background=True,
                )

                await UniMessage().image(raw=rank_img).send(target)


@weather_rank_helper.handle()
async def _() -> None:
    with open(Path(__file__).parent / 'help.md', 'r', encoding='utf-8') as f:
        md: str = f.read()
    help_img: bytes = await md_to_pic(md=md, width=720)
    msg: UniMessage[Image] = UniMessage().image(raw=help_img)
    await weather_rank_helper.finish(msg)


@weather_rank.handle()
async def _(event: Event, result: Arparma) -> None:
    dbs: DBService = DBService.get_instance()
    await dbs.init()
    id: int = int(UniMessage.get_target(event).id)

    if '添加城市' in result.subcommands:
        # 如果匹配至'添加城市'子命令，则通过api获取城市地区码，并写入数据库
        city: str = result.subcommands['添加城市'].args['city']
        async with httpx.AsyncClient() as ctx:
            res = await ctx.get(
                f'{CITY_SEARCH_BASE_URL}location={city}&key={plugin_config.qweather_api_key}'
            )
            if res.status_code == 200:
                data = res.json()['location']
                if data and len(data) > 0:
                    location_code: str = data[0]['id']
                    location_name: str = data[0]['name']
                    msg1: str = await dbs.add_location_for_group(
                        id, location_code, location_name
                    )
                    await weather_rank.finish(msg1)
            else:
                await weather_rank.finish('城市名称错误')

    if '删除城市' in result.subcommands:
        # 如果匹配至'删除城市'子命令，则通过api获取城市地区码，从数据库删除
        del_city: str = result.subcommands['删除城市'].args['city']
        async with httpx.AsyncClient() as ctx:
            res = await ctx.get(
                f'{CITY_SEARCH_BASE_URL}location={del_city}&key={plugin_config.qweather_api_key}'
            )
            if res.status_code == 200:
                data = res.json()['location']
                logger.error(data)
                if data and len(data) > 0:
                    location_code = data[0]['id']
                    location_name = data[0]['name']
                    d_msg: str = await dbs.remove_location_from_group(id, location_code)
                    await weather_rank.finish(d_msg)
            else:
                await weather_rank.finish('城市名称错误')

    if '排行榜' in result.subcommands:
        # 如果匹配至'排行榜'，则通过api获取当日订阅地区的实时/近7日气温(由具体模式决定)
        mode: str = result.subcommands['排行榜'].args['mode']
        if mode not in ['气温', '温差']:
            await weather_rank.finish('不支持的排行榜')
        locations: list[LocationInfo] = await dbs.get_locations_in_group(id)
        weathers: list[WeatherData] = []
        for location in locations:
            async with httpx.AsyncClient() as ctx:
                response: httpx.Response = await ctx.get(
                    f'{NOW_WEATHER_SEARCH_BASE_URL}location={location.code}&key={plugin_config.qweather_api_key}'
                    if mode == '气温'
                    else f'{DAILY_WEATHER_SEARCH_BASE_URL}location={location.code}&key={plugin_config.qweather_api_key}'
                )
                if response.status_code == 200:
                    if mode == '气温':
                        now_weather: NowWeather = NowWeather(**response.json())
                        weathers.append(
                            WeatherData(name=location.name, temp=now_weather.now.temp)
                        )
                    elif mode == '温差':
                        daily_weather: DailyWeather = DailyWeather(**response.json())
                        weathers.append(
                            WeatherData(
                                name=location.name,
                                temp=str(
                                    int(daily_weather.daily[0].temp_max)
                                    - int(daily_weather.daily[0].temp_min)
                                ),
                            )
                        )
                else:
                    await weather_rank.send(f'获取{location.name}天气信息失败')
        # 对各地气温/温差进行排序
        weathers.sort(key=lambda x: int(x.temp), reverse=True)

        # 绘制排行榜
        template_path: str = str(Path(__file__).parent / 'templates')
        template_name: str = 'rank_card.html.jinja2'

        await weather_rank.send('正在生成排行榜……')
        rank_img: bytes = await template_element_to_pic(
            template_path,
            template_name,
            templates={'datas': weathers, 'mode': mode},
            element='.container',
            wait=2,
            omit_background=True,
        )

        msg2: UniMessage[Image] = UniMessage().image(raw=rank_img)
        await weather_rank.finish(msg2)

    if '气温地图' in result.subcommands:
        # 如果匹配至'气温地图'，则爬取中国天气网的气温地图并发送
        await weather_rank.send('正在获取气温地图……')
        url = ''
        async with httpx.AsyncClient() as ctx:
            res = await ctx.get(TEMPERATURE_MAP_BASE_URL)
            if res.status_code == 200:
                soup = BeautifulSoup(res.text, 'html.parser')
                img_element: Tag | None = soup.select_one('.imgblock > img')
                logger.info(f'img_ele: {img_element}')
                if img_element:
                    img_url: str | list[str] | None = img_element.get('src')
                    if isinstance(img_url, str):
                        url = img_url
        if len(url) > 0:
            msg = UniMessage().image(url=url)
            await weather_rank.finish(msg)
        else:
            msgg = UniMessage().text('获取图片失败')
            await weather_rank.finish(msgg)

    if '当地天气' in result.subcommands:
        # 如果匹配至'当地天气'，则获取该地气温并绘制当地天气图
        query_city: str = result.subcommands['当地天气'].args['city']
        async with httpx.AsyncClient() as ctx:
            location_c: str = ''
            location_n: str = ''
            res1: httpx.Response = await ctx.get(
                f'{CITY_SEARCH_BASE_URL}location={query_city}&key={plugin_config.qweather_api_key}'
            )
            if res1.status_code == 200:
                data = res1.json()['location']
                if data and len(data) > 0:
                    location_c = data[0]['id']
                    location_n = data[0]['name']
            if location_c != '' and location_n != '':
                res2: httpx.Response = await ctx.get(
                    f'{NOW_WEATHER_SEARCH_BASE_URL}location={location_c}&key={plugin_config.qweather_api_key}'
                )
                now_wea: NowWeather = NowWeather(**res2.json())
                res3: httpx.Response = await ctx.get(
                    f'{DAILY_WEATHER_SEARCH_BASE_URL}location={location_c}&key={plugin_config.qweather_api_key}'
                )
                daily_wea: DailyWeather = DailyWeather(**res3.json())
                res4: httpx.Response = await ctx.get(
                    f'{HOURLY_WEATHER_SEARCH_BASE_URL}location={location_c}&key={plugin_config.qweather_api_key}'
                )
                hourly_wea: HourlyWeather = HourlyWeather(**res4.json())
                res5: httpx.Response = await ctx.get(
                    f'{AIR_QUALITY_BASE_URL}location={location_c}&key={plugin_config.qweather_api_key}'
                )
                air_quality = res5.json()['now']

                future_hourly_weathers: list[FutureHourlyWeatherItem] = []
                future_daily_weathers: list[FutureDailyWeatherItem] = []

                for index, hourly_data in enumerate(hourly_wea.hourly):
                    if index == 6:
                        break
                    time: int = datetime.fromisoformat(hourly_data.fx_time).hour
                    future_hourly_weathers.append(
                        FutureHourlyWeatherItem(
                            time=str(time), icon=hourly_data.icon, temp=hourly_data.temp
                        )
                    )

                for daily_data in daily_wea.daily:
                    date_obj = datetime.strptime(daily_data.fx_date, '%Y-%m-%d')
                    weekday_index: int = date_obj.weekday()
                    weekdays: list[str] = [
                        '周一',
                        '周二',
                        '周三',
                        '周四',
                        '周五',
                        '周六',
                        '周日',
                    ]
                    future_daily_weathers.append(
                        FutureDailyWeatherItem(
                            week_day=weekdays[weekday_index],
                            icon=daily_data.icon_day,
                            min_temp=daily_data.temp_min,
                            max_temp=daily_data.temp_max,
                            left_width=str(
                                round((int(daily_data.temp_min) + 40) / 85 * 100)
                            ),
                            right_width=str(
                                round((45 - int(daily_data.temp_max)) / 85 * 100)
                            ),
                        )
                    )

                weather_card_data: WeatherCardData = WeatherCardData(
                    location=location_n,
                    now_temp=now_wea.now.temp,
                    max_temp=daily_wea.daily[0].temp_max,
                    min_temp=daily_wea.daily[0].temp_min,
                    now_text=now_wea.now.text,
                    aqi=air_quality['aqi'],
                    air_category=air_quality['category'],
                    future_hourly_weather=future_hourly_weathers,
                    future_daily_weather=future_daily_weathers,
                )

                # 绘制天气图
                template_p: str = str(Path(__file__).parent / 'templates')
                template_n: str = 'weather_card.html.jinja2'

                await weather_rank.send('正在生成天气图……')
                weather_img: bytes = await template_element_to_pic(
                    template_p,
                    template_n,
                    templates={'data': weather_card_data},
                    element='.container',
                    wait=2,
                    omit_background=True,
                )

                msg3: UniMessage[Image] = UniMessage().image(raw=weather_img)
                await weather_rank.finish(msg3)

    if '订阅' in result.subcommands:
        m: str = await dbs.add_subscribed_group(id)
        await weather_rank.finish(m)

    if '取消订阅' in result.subcommands:
        _m: str = await dbs.remove_subscribed_group(id)
        await weather_rank.finish(_m)
