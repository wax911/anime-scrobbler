import argparse
from anilist import HttpController
import app, nyaa, plex


def __description() -> str:
    return "Just another anime scrobbler.."


def __usage() -> str:
    return "manage.py --test anilist" + \
           "\n" + \
           "manage.py --test nyaa" + \
           "\n" + \
           "manage.py --test plex" + \
           "\n" + \
           "manage.py --run app"


def __init_cli() -> argparse:
    parser = argparse.ArgumentParser(description=__description(), usage=__usage())
    parser.add_argument('-t', '--test', default='anilist',
                        help="test different modules")
    parser.add_argument('-r', '--run', default='app',
                        help="run the production module")
    return parser


def __print_program_end() -> None:
    print("-----------------------------------")
    print("End of execution")
    print("-----------------------------------")


def __init_app(args: argparse) -> None:
    test = args.test
    run = args.run
    if test is not None:
        if test == 'anilist':
            HttpController().make_request()
        elif test == 'nyaa':
            pass
        elif test == 'plex':
            pass
    elif run is not None:
        if run == 'app':
            pass
    else:
        print()
        print("For instructions on how to use this program, please run:\nmanage.py --help")


if __name__ == '__main__':
    cli_args = __init_cli().parse_args()
    __init_app(cli_args)
