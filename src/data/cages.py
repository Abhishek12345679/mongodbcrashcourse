import datetime

import mongoengine

from data.bookings import Booking


class Cage(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    price = mongoengine.FloatField(required=True)
    square_meters = mongoengine.FloatField(required=True)
    is_carpeted = mongoengine.BooleanField(default=True)
    allows_dangerous_snakes = mongoengine.BooleanField(default=False)

    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta_data = {
        "alias": "core",
        "collection": "cages"
    }
