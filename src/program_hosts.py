import datetime
import re

from colorama import Fore
from dateutil import parser

import infrastructure.state as state
import services.data_service as svc
from infrastructure.switchlang import switch


def run():
    print(' ****************** Welcome  host **************** ')
    print()

    show_commands()

    while True:
        action = get_action()

        with switch(action) as s:
            s.case('c', create_account)
            s.case('a', log_into_account)
            s.case('l', list_cages)
            s.case('r', register_cage)
            s.case('u', update_availability)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')
            s.case(['x', 'bye', 'exit', 'exit()'], exit_app)
            s.case('?', show_commands)
            s.case('', lambda: None)
            s.default(unknown_command)

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('Login to your [a]ccount')
    print('[L]ist your cages')
    print('[R]egister a cage')
    print('[U]pdate cage availability')
    print('[V]iew your bookings')
    print('Change [M]ode (guest or host)')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def create_account():
    print(' ****************** REGISTER **************** ')
    name = input('Enter your Name : ')

    emailregex = re.compile(r'^([a-zA-Z0-9_\-.]+)@([a-zA-Z0-9_\-.]+)\.([a-zA-Z]{2,5})$')
    email = emailregex.search(input('Enter your Email : ').strip().lower())

    if not email:
        error_msg(f'Not an Email')
        return

    old_account = svc.find_account_by_email(email.group())
    if old_account:
        error_msg(f'Account with email - {email} already exists.')
        return

    state.active_account = svc.create_account(name, email.group())
    success_msg(
        f'New Account {state.active_account.id} with email - {email.group()} created at {datetime.datetime.now()}')


def log_into_account():
    print(' ****************** LOGIN **************** ')

    emailregex = re.compile(r'^([a-zA-Z0-9_\-.]+)@([a-zA-Z0-9_\-.]+)\.([a-zA-Z]{2,5})$')
    email = emailregex.search(input('Enter your Email : ').strip().lower())

    if not email:
        error_msg(f'Not an Email')
        return

    account = svc.find_account_by_email(email.group())

    if not account:
        success_msg(f'could not find User with email {email.group()}')
        return

    state.active_account = account
    success_msg(f'Logged in with no issues.')


def register_cage():
    print(' ****************** REGISTER CAGE **************** ')

    active_account = state.active_account
    if not active_account:
        error_msg(f'Please Login or create a new account : - ')
        return

    meters = input("How many square meters is the Cage ?")
    if not meters:
        error_msg(f'Enter the Cage Size in sq.mts ')
        return

    meters = float(meters)
    carpeted = input("Is it carpeted [y, n]? ").lower().startswith('y')
    has_toys = input("Have snake toys [y, n]? ").lower().startswith('y')
    allow_dangerous = input(
        "Can you host venomous snakes [y, n]? ").lower().startswith('y')
    name = input("Give your cage a name: ")
    price = float(input("How much is a noit ?"))

    cage = svc.register_cage(
        state.active_account, name,
        allow_dangerous, has_toys, carpeted, meters,
        price
    )

    state.reload_account()
    success_msg(f'Cage registered with ID {cage.id}')


def list_cages(supress_header=False):
    if not supress_header:
        print(' ******************     Your cages     **************** ')

    active_account = state.active_account

    if not active_account:
        error_msg(f'Please Login or create a new account : - ')
        return

    cages = svc.find_cages_for_user(active_account)
    print(f'You have {len(cages)} cages.\n')
    for idx, c in enumerate(cages):
        print(f'Cage {idx + 1}')
        print(f'Name - {c.name}')
        print(f'Floor Size - {c.meters}')
        print(f'Carpeted - {c.carpeted}')
        print(f'Are there any Venomous Snakes - {c.allows_dangerous}')
        print(f'Does It have Toys - {c.has_toys}')
        print(f'One night = ${c.price}\n')
        for b in c.bookings:
            success_msg('      * Booking: {}, {} days, booked? {}'.format(
                b.check_in_date,
                (b.check_out_date - b.check_in_date).days,
                'YES' if b.booked_date is not None else 'no'
            ))


def update_availability():
    print(' ****************** Add available date **************** ')

    active_account = state.active_account

    if not active_account:
        error_msg(f'Please Login or create a new account : - ')
        return

    list_cages(supress_header=True)

    cagenumber = input('Book a Cage ?')
    if not cagenumber.strip():
        error_msg('Cancelled')
        print()

    cagenumber = int(cagenumber)
    account_cages = svc.find_cages_for_user(active_account)

    selectedcage = account_cages[cagenumber - 1]

    start_date = parser.parse(input('Enter available venom time slots?'))
    duration = int(input("How long can a stay be ? "))

    svc.add_available_date(selectedcage, start_date, duration)
    state.reload_account()

    success_msg(f'Date Added at {start_date} for {selectedcage.name}')


def view_bookings():
    print(' ****************** Your bookings **************** ')

    # TODO: Require an account
    # TODO: Get cages, and nested bookings as flat list
    # TODO: Print details for each

    print(" -------- NOT IMPLEMENTED -------- ")


def exit_app():
    print()
    print('bye')
    raise KeyboardInterrupt()


def get_action():
    text = '> '
    if state.active_account:
        text = f'{state.active_account.name}> '

    action = input(Fore.YELLOW + text + Fore.WHITE)
    return action.strip().lower()


def unknown_command():
    print("Sorry we didn't understand that command.")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
