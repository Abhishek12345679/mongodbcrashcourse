import mongoengine
import datetime


class Snake(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    species = mongoengine.StringField(required=True)

    length = mongoengine.FloatField(required=True, min_value=0.001)
    name = mongoengine.StringField(required=True)
    is_venomous = mongoengine.BooleanField(default=False)

    meta_data = {
        "alias": "core",
        "collection": "snakes"
    }
