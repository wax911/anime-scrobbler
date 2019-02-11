import argparse
from anilist import AniListController, MediaTitle
from plex import PlexController
from nyaa import NyaaController


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
    parser.add_argument('-t', '--test', default='nyaa',
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
            AniListController().make_request()
        elif test == 'nyaa':
            NyaaController.search_for_show(MediaTitle(
                english='The Rising of the Shield Hero',
                romaji='Tate no Yuusha no Nariagari',
                native='盾の勇者の成り上がり',
                userPreferred='Tate no Yuusha no Nariagari'
            ))
        elif test == 'plex':
            PlexController().find_all_by_title('Anime')
    elif run is not None:
        if run == 'app':
            pass
    else:
        print()
        print("For instructions on how to use this program, please run:\nmanage.py --help")


if __name__ == '__main__':
    cli_args = __init_cli().parse_args()
    __init_app(cli_args)
