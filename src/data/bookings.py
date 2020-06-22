import mongoengine
import datetime


class Booking(mongoengine.EmbeddedDocument):
    guest_owner_id = mongoengine.ObjectIdField()
    guest_snake_id = mongoengine.ObjectIdField()

    booked_date = mongoengine.DateTimeField()
    check_in_date = mongoengine.DateTimeField(default=datetime.datetime.now)
    check_out_date = mongoengine.DateTimeField(default=datetime.datetime.now)

    review = mongoengine.StringField(required=False)
    ratings = mongoengine.FloatField(default=0.0)
