from colorama import Fore
from dateutil import parser

import infrastructure.state as state
import program_hosts as hosts
import services.data_service as svc
from infrastructure.switchlang import switch


def run():
    print(' ****************** Welcome guest **************** ')
    print()

    show_commands()

    while True:
        action = hosts.get_action()

        # there is no default switch smt. in python ,
        # so this is a library by @michaelkennedy

        with switch(action) as s:
            s.case('c', hosts.create_account)
            s.case('l', hosts.log_into_account)

            s.case('a', add_a_snake)
            s.case('y', view_your_snakes)
            s.case('b', book_a_cage)
            s.case('v', view_bookings)
            s.case('m', lambda: 'change_mode')

            s.case('?', show_commands)
            s.case('', lambda: None)
            s.case(['x', 'bye', 'exit', 'exit()'], hosts.exit_app)

            s.default(hosts.unknown_command)

        state.reload_account()

        if action:
            print()

        if s.result == 'change_mode':
            return


def show_commands():
    print('What action would you like to take:')
    print('[C]reate an account')
    print('[L]ogin to your account')
    print('[B]ook a cage')
    print('[A]dd a snake')
    print('View [y]our snakes')
    print('[V]iew your bookings')
    print('[M]ain menu')
    print('e[X]it app')
    print('[?] Help (this info)')
    print()


def add_a_snake():
    print(' ****************** Add a snake **************** ')

    account = state.active_account
    if not account:
        error_msg(f'Please Login or create an account')
        return

    name = input('What is your snake\'s name ? ')
    length = float(input('How long is your snake ?'))
    is_venomous = input('Is it venomous ?').lower().startswith("y")
    species = input('What species ?')

    snake = svc.add_snake(account, name, length, is_venomous, species)
    state.reload_account()
    success_msg(f'{snake.name} ({snake.id}) added to our snake directory')


def view_your_snakes():
    print(' ****************** Your snakes **************** ')

    account = state.active_account
    if not account:
        error_msg(f'Please Login or create an account')
        return

    snakes = svc.get_snakes_for_user(account.id)
    for idx, c in enumerate(snakes):
        print(f'{idx + 1}.')
        print(f'{c.name}')
        print(f'sp.{c.species}')
        if c.is_venomous:
            success_msg(f'Venomous\n')
        else:
            error_msg(f'Venomous')
        print(f'Length: {c.length}\n')


def book_a_cage():
    print(' ****************** Book a cage **************** ')

    account = state.active_account
    if not account:
        error_msg(f'Please Login or create an account')
        return

    # has_snake = account.snake_ids
    snakes = svc.get_snakes_for_user(account.id)

    if not snakes:
        error_msg('Add a snake to continue')
        return

    view_your_snakes()

    selected_snake = snakes[int(input("select the snake you want to book for - ")) - 1]

    start_date = input("Enter the Check-in date in the format :- (dd-mm-yyyy) :- ")

    if not start_date:
        error_msg('cancelled')
        return

    check_in_date = parser.parse(start_date)

    end_date = input("Enter the Check-out date in the format :- (dd-mm-yyyy) :- ")

    if not end_date:
        error_msg('cancelled')
        return

    check_out_date = parser.parse(end_date)

    if check_out_date <= check_in_date:
        print('Sorry! Checkout date cannot be earlier than checkin date')
        return

    cages = svc.find_available_cages(selected_snake, check_in_date, check_out_date)

    print("There are {} cages available in that time.".format(len(cages)))
    for idx, c in enumerate(cages):
        print(" {}. {} with {}m carpeted: {}, has toys: {}.".format(
            idx + 1,
            c.name,
            c.square_meters,
            'yes' if c.is_carpeted else 'no',
            'yes' if c.has_toys else 'no'))

    if not cages:
        error_msg("Sorry, no cages are available for that date.")
        return

    cage = cages[int(input('Which cage do you want to book (number)')) - 1]
    svc.book_cage(state.active_account, selected_snake, cage, check_in_date, check_out_date)

    success_msg('Successfully booked {} for {} at ${}/night.'.format(cage.name, selected_snake.name, cage.price))


def view_bookings():
    print(' ****************** Your bookings **************** ')
    # TODO: Require an account
    # TODO: List booking info along with snake info

    print(" -------- NOT IMPLEMENTED -------- ")


def success_msg(text):
    print(Fore.LIGHTGREEN_EX + text + Fore.WHITE)


def error_msg(text):
    print(Fore.LIGHTRED_EX + text + Fore.WHITE)
