import datetime

import mongoengine

from data.bookings import Booking


class Cage(mongoengine.Document):
    registered_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    name = mongoengine.StringField(required=True)
    allows_dangerous = mongoengine.BooleanField(default=False)
    has_toys = mongoengine.BooleanField(default=True)
    price = mongoengine.FloatField(required=True)
    meters = mongoengine.FloatField(required=True)
    carpeted = mongoengine.BooleanField(default=True)

    bookings = mongoengine.EmbeddedDocumentListField(Booking)

    meta_data = {
        "alias": "core",
        "collection": "cages"
    }
