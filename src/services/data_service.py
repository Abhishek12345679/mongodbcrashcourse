import datetime
from typing import List

import bson
from mongoengine.queryset.visitor import Q

from data.bookings import Booking
from data.cages import Cage
from data.owners import Owner
from data.snakes import Snake


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


def add_available_date(selectedcage: Cage, start_date: datetime.datetime, duration: int):
    booking = Booking()
    booking.check_in_date = start_date
    booking.check_out_date = start_date + datetime.timedelta(days=duration)

    cage = Cage.objects(id=selectedcage.id).first()
    cage.bookings.append(booking)
    cage.save()

    return cage


def add_snake(account: Owner, name: str, length: float, is_venomous: bool, species: str):
    snake = Snake()
    snake.name = name
    snake.length = length
    snake.is_venomous = is_venomous
    snake.species = species
    snake.save()

    owner = find_account_by_email(account.email)
    owner.snake_ids.append(snake.id)
    owner.save()

    return snake


def get_snakes_for_user(user_id: bson.ObjectId) -> List[Snake]:
    owner = Owner.objects(id=user_id).first()
    snakes = Snake.objects(id__in=owner.snake_ids).all()

    return list(snakes)


def find_available_cages(snake: Snake, checkin: datetime.datetime,
                         checkout: datetime.datetime) -> List[Cage]:
    min_size = 0

    query = Cage.objects() \
        .filter(meters__gte=min_size) \
        .filter(bookings__check_in_date__lte=checkin) \
        .filter(bookings__check_out_date__gte=checkout)

    if snake.is_venomous:
        query = query.filter(allows_dangerous=True)

    cages = query.order_by('price', 'meters')

    final_cages = []
    for c in cages:
        for b in c.bookings:
            if b.check_in_date <= checkin and b.check_out_date >= checkout and b.guest_snake_id is None:
                final_cages.append(c)

    return final_cages


def book_cage(active_account: Owner, selected_snake: Snake, cage: Cage, check_in_date: datetime.datetime,
              check_out_date: datetime.datetime):
    booking: Booking = None

    for b in cage.bookings:
        if b.check_in_date <= check_in_date \
                and b.check_out_date >= check_out_date \
                and b.guest_snake_id is None:
            booking = b
            break

    booking.booked_date = datetime.datetime.now()
    booking.check_in_date = check_in_date
    booking.check_out_date = check_out_date
    booking.guest_snake_id = selected_snake.id
    booking.guest_owner_id = active_account.id

    cage.save()


def get_bookings_for_user(email: str) -> List[Booking]:
    account = find_account_by_email(email)

    booked_cages = Cage.objects() \
        .filter(bookings__guest_owner_id=account.id) \
        .only('bookings', 'name')

    def map_cage_to_booking(cage, booking):
        booking.cage = cage
        return booking

    bookings = [
        map_cage_to_booking(cage, booking)
        for cage in booked_cages
        for booking in cage.bookings
        if booking.guest_owner_id == account.id
    ]

    return bookings
