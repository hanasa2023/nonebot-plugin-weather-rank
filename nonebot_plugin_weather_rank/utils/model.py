from __future__ import annotations

from pydantic import BaseModel, Field


class Now(BaseModel):
    obs_time: str = Field(..., alias='obsTime')
    temp: str = Field(...)
    feels_like: str = Field(..., alias='feelsLike')
    icon: str = Field(...)
    text: str = Field(...)
    wind360: str = Field(...)
    wind_dir: str = Field(..., alias='windDir')
    wind_scale: str = Field(..., alias='windScale')
    wind_speed: str = Field(..., alias='windSpeed')
    humidity: str = Field(...)
    precip: str = Field(...)
    pressure: str = Field(...)
    vis: str = Field(...)
    cloud: str | None = Field(None)
    dew: str | None = Field(None)


class Daily(BaseModel):
    fx_date: str = Field(..., alias='fxDate')
    sunrise: str | None = Field(None)
    sunset: str | None = Field(None)
    moonrise: str | None = Field(None)
    moonset: str | None = Field(None)
    moon_phase: str = Field(..., alias='moonPhase')
    moon_phase_icon: str = Field(..., alias='moonPhaseIcon')
    temp_max: str = Field(..., alias='tempMax')
    temp_min: str = Field(..., alias='tempMin')
    icon_day: str = Field(..., alias='iconDay')
    text_day: str = Field(..., alias='textDay')
    icon_night: str = Field(..., alias='iconNight')
    text_night: str = Field(..., alias='textNight')
    wind360_day: str = Field(..., alias='wind360Day')
    wind_dir_day: str = Field(..., alias='windDirDay')
    wind_scale_day: str = Field(..., alias='windScaleDay')
    wind_speed_day: str = Field(..., alias='windSpeedDay')
    wind360_night: str = Field(..., alias='wind360Night')
    wind_dir_night: str = Field(..., alias='windDirNight')
    wind_scale_night: str = Field(..., alias='windScaleNight')
    wind_speed_night: str = Field(..., alias='windSpeedNight')
    precip: str = Field(...)
    uv_index: str = Field(..., alias='uvIndex')
    humidity: str = Field(...)
    pressure: str = Field(...)
    vis: str = Field(...)
    cloud: str | None = Field(None)


class Hourly(BaseModel):
    fx_time: str = Field(..., alias='fxTime')
    temp: str = Field(...)
    icon: str = Field(...)
    text: str = Field(...)
    wind360: str = Field(...)
    wind_dir: str = Field(..., alias='windDir')
    wind_scale: str = Field(..., alias='windScale')
    wind_speed: str = Field(..., alias='windSpeed')
    humidity: str = Field(...)
    precip: str = Field(...)
    pop: str | None = Field(None)
    pressure: str = Field(...)
    cloud: str | None = Field(None)
    dew: str | None = Field(None)


class Refer(BaseModel):
    sources: list[str] | None = Field(None)
    license: list[str] | None = Field(None)


class NowWeather(BaseModel):
    code: str = Field(...)
    update_time: str = Field(..., alias='updateTime')
    fx_link: str = Field(..., alias='fxLink')
    now: Now = Field(...)
    refer: Refer = Field(...)


class DailyWeather(BaseModel):
    code: str = Field(...)
    update_time: str = Field(..., alias='updateTime')
    fx_link: str = Field(..., alias='fxLink')
    daily: list[Daily] = Field(...)
    refer: Refer = Field(...)


class HourlyWeather(BaseModel):
    code: str = Field(...)
    update_time: str = Field(..., alias='updateTime')
    fx_link: str = Field(..., alias='fxLink')
    hourly: list[Hourly] = Field(...)
    refer: Refer = Field(...)


class WeatherData(BaseModel):
    name: str
    temp: str


class FutureHourlyWeatherItem(BaseModel):
    time: str
    icon: str
    temp: str


class FutureDailyWeatherItem(BaseModel):
    week_day: str
    icon: str
    min_temp: str
    max_temp: str
    left_width: str
    right_width: str


class WeatherCardData(BaseModel):
    location: str
    now_temp: str
    max_temp: str
    min_temp: str
    now_text: str
    aqi: str
    air_category: str
    future_hourly_weather: list[FutureHourlyWeatherItem]
    future_daily_weather: list[FutureDailyWeatherItem]
