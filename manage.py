import inspect
import argparse
from app import AppController
from app.util.io import EventLogHelper

LIST_KEY_CURRENT = "CURRENT"
LIST_KEY_PLANNING = "PLANNING"
LIST_KEY_COMPLETED = "COMPLETED"
LIST_KEY_PAUSED = "PAUSED"
LIST_KEY_REPEATING = "REPEATING"


def __description() -> str:
    return "Just a little utility for research purposes (wink, wink).."


def __usage() -> str:
    return f"manage.py --from-list list_name_1, list_name_2\n\n" \
        f"Where list_name is one of the following:\n" \
        f"{LIST_KEY_CURRENT}, {LIST_KEY_PLANNING}, {LIST_KEY_COMPLETED}, {LIST_KEY_PAUSED}, {LIST_KEY_REPEATING}\n"


def __init_cli() -> argparse:
    parser = argparse.ArgumentParser(description=__description(), usage=__usage())
    parser.add_argument('-fl', '--from-list', default=LIST_KEY_CURRENT,
                        help="Run the utility and download torrent files in the defined list types")
    return parser


def __print_program_end() -> None:
    print("-----------------------------------")
    print("End of execution")
    print("-----------------------------------")


def __init_app(args: argparse) -> None:
    if args.from_list is not None:
        print('\n----------------       Anime Scrobbler        -------------------\n')
        EventLogHelper.log_info(f"Starting application with parameter agr.from_list -> {args.from_list}",
                                __name__,
                                inspect.currentframe().f_code.co_name)
        AppController(args.from_list).start_application()
    else:
        print()
        print("For instructions on how to use this program, please run:\nmanage.py --help")


if __name__ == '__main__':
    cli_args = __init_cli().parse_args()
    __init_app(cli_args)
