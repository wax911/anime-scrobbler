from typing import Optional

from anilist import AniListController, MediaTitle
from anilist.data import PickleStore as AniListStore
from plex import PlexController
from nyaa import NyaaController

from ..data import AppState, PickleStore as AppStore


class AppController:

    def __init__(self, list_name: str) -> None:
        super().__init__()
        self.list_name = list_name
        self.anilist_controller = AniListController()
        self.plex_controller = PlexController()
        self.nyaa_controller = NyaaController()

    def fetch_anime_list(self):
        """
        Fetches a list of
        :return:
        """
        self.anilist_controller.make_request()
        AniListStore().get(self.list_name)

    def find_plex_show(self, media_title: MediaTitle) -> Optional[AppState]:
        """
        Fetches a list of shows by title if they exist, if not an empty collection would be returned
        :param media_title: a model consisting of various anime names from anilist
        :return: an optional AppState
        """
        self.plex_controller.find_all_by_title('')
        return None

    def search_nyaa_for_show(self, media_title: MediaTitle):
        """
        Searches nyaa.si for torrents matching the tittle name/s
        :param media_title: a model consisting of various anime names from anilist
        :return: a list of torrent results
        """
        self.nyaa_controller.search_for_show(media_title)

    def start_application(self):
        pass
