import datetime
from typing import List

from mongoengine.queryset.visitor import Q

from data.bookings import Booking
from data.cages import Cage
from data.owners import Owner


def create_account(name: str, email: str) -> Owner:
    owner = Owner()
    owner.name = name
    owner.email = email

    owner.save()

    return owner


def find_account_by_email(email: str) -> Owner:
    owner = Owner.objects().get(Q(email=email))
    if owner:
        return owner
    else:
        return None


def register_cage(active_account: Owner, name,
                  allow_dangerous, has_toys, carpeted, meters, price) -> Cage:
    cage = Cage()
    cage.name = name
    cage.allow_dangerous = allow_dangerous
    cage.has_toys = has_toys
    cage.carpeted = carpeted
    cage.meters = meters
    cage.price = price

    cage.save()

    account = find_account_by_email(active_account.email)
    account.cage_ids.append(cage.id)
    account.save()

    return cage


def find_cages_for_user(account: Owner) -> List[Cage]:
    query = Cage.objects(id__in=account.cage_ids)
    cages = list(query)

    return cages


def add_available_date(
        selectedcage: Cage,
        start_date: datetime.datetime,
        duration: int):
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=duration)

    cage = Cage.objects(id=selectedcage.id).first()
    cage.bookings.append(booking)
    cage.save()

    return cage
