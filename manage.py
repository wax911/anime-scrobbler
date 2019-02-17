import argparse
from typing import List

from app import AppController
from anilist.data import LIST_KEY_CURRENT, LIST_KEY_PLANNING, LIST_KEY_COMPLETED, LIST_KEY_PAUSED, LIST_KEY_REPEATING


def __description() -> str:
    return "Just a little utility for research purposes (wink, wink).."


def __usage() -> str:
    return f"manage.py --from-list list_name_1, list_name_2\n\n" \
        f"Where list_name is one or more of the following:\n" \
        f"{LIST_KEY_CURRENT}, {LIST_KEY_PLANNING}, {LIST_KEY_COMPLETED}, {LIST_KEY_PAUSED}, {LIST_KEY_REPEATING}\n"


def __init_cli() -> argparse:
    parser = argparse.ArgumentParser(description=__description(), usage=__usage())
    parser.add_argument('-fl', '--from-list', default=LIST_KEY_CURRENT, type=List,
                        help="Run the utility and download torrent files in the defined list types")
    return parser


def __print_program_end() -> None:
    print("-----------------------------------")
    print("End of execution")
    print("-----------------------------------")


def __init_app(args: argparse) -> None:
    if args.run is not None:
        AppController(args.run).start_application()
    else:
        print()
        print("For instructions on how to use this program, please run:\nmanage.py --help")


if __name__ == '__main__':
    cli_args = __init_cli().parse_args()
    __init_app(cli_args)
