from tortoise import fields
from tortoise.models import Model


class Weather(Model):
    id = fields.IntField(True, generated=True)
    group_id = fields.TextField()
    location_code = fields.TextField()
    location_name = fields.TextField()


class WeatherSubscribed(Model):
    id = fields.IntField(True, generated=True)
    group_id = fields.IntField(unique=True)
