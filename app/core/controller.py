import inspect
import json

from typing import Optional, List, Tuple
from dacite import from_dict
from tinydb import where

from anilist import AniListController, MediaTitle, MediaEntry, AniListStore
from app import EventLogHelper
from nyaa import NyaaController, TorrentInfo, AppConfig, NyaaModelHelper
from plex import PlexController, Show, Episode
from ..data import AppStore
from ..util import StorageUtil


class AppController:

    def __init__(self, list_name: str) -> None:
        super().__init__()
        self.list_name = list_name
        self.anilist_search_query = (where('status') == list_name)
        self.anilist_controller: AniListController = AniListController()
        self.plex_controller: PlexController = PlexController()
        self.nyaa_controller: NyaaController = NyaaController()
        self.app_store: AppStore = AppStore()
        self.app_config = self.__get_app_configuration()

    @staticmethod
    def __get_app_configuration() -> AppConfig:
        json_string = json.loads(StorageUtil.read_file('config', 'app.json'))
        return from_dict(AppConfig, json_string)

    def __search_for_anime_by_title(self, show_title: str, media_entries: List[MediaEntry]) -> MediaEntry:
        """
        Find anilist shows matching the show title in plex
        :param show_title:
        :param media_entries:
        :return:
        """
        for media_entry in media_entries:
            media_title: MediaTitle = media_entry.media.title
            if media_title.romaji == show_title or media_title.english == show_title:
                EventLogHelper.log_info(f"Search match found -> {show_title}",
                                        self.__class__.__name__,
                                        inspect.currentframe().f_code.co_name)
                return media_entry

    def fetch_anime_list(self) -> List[Optional[MediaEntry]]:
        """
        Fetches a media group of anime by the passed list name
        :return: list of anime of the group
        """
        anilist_store: AniListStore = AniListStore()
        if self.list_name is not None:
            self.anilist_controller.make_request(anilist_store)
        media_list_entries = anilist_store.search(self.anilist_search_query)
        return media_list_entries

    def find_plex_show(self, media_entries: List[MediaEntry]) -> List[Optional[Show]]:
        """
        Fetches a list of shows by title if they exist, if not an empty collection would be returned
        :param media_entries: a model consisting of various anime names from anilist
        :return: a list of optional shows
        """
        download_list: List[Optional[Show]] = list()
        for entry in media_entries:
            if entry.media.status != 'NOT_YET_RELEASED':
                show = self.plex_controller.find_all_by_title(entry.media.title)
                download_list += show
        EventLogHelper.log_info(f"Fetched list of shows by title, returned {download_list.__len__()} results",
                                self.__class__.__name__,
                                inspect.currentframe().f_code.co_name)
        return download_list

    def find_missing_show_entries(self, shows: List[Optional[Show]], entries: List[MediaEntry]) -> \
            Tuple[List[Optional[Show]], List[Optional[MediaEntry]]]:
        """
        Compares the number of available episodes in each season with those on anilist
        :param shows:
        :param entries:
        :return: tuple of corresponding shows and media entries
        """
        shows_with_missing_episodes: List[Optional[Show]] = list()
        media_entry_with_missing_episodes: List[Optional[MediaEntry]] = list()
        for show in shows:
            media_entry: MediaEntry = self.__search_for_anime_by_title(show.title, entries)
            if media_entry is not None:
                episodes: List[Optional[Episode]] = show.episodes()
                if media_entry.media.episodes is not None:
                    if media_entry.media.episodes > episodes.__len__():
                        shows_with_missing_episodes.append(show)
                        media_entry_with_missing_episodes.append(media_entry)
                elif media_entry.media.status == 'RELEASING':
                    shows_with_missing_episodes.append(show)
                    media_entry_with_missing_episodes.append(media_entry)
        return shows_with_missing_episodes, media_entry_with_missing_episodes

    def search_nyaa_for_shows(self, show_media_tuple: Tuple[List[Optional[Show]], List[Optional[MediaEntry]]]) -> \
            Optional[List[TorrentInfo]]:
        """
        Searches nyaa.si for torrents matching the tittle name/s
        :param show_media_tuple: a model consisting of a tuple shows and media entries of missing episodes
        :return: a list of torrent results
        """
        torrent_search_result_list: List[TorrentInfo] = list()
        show_list, media_list = show_media_tuple
        for show, media in zip(show_list, media_list):
            EventLogHelper.log_info(f"Searching nyaa.si for -> {show.title} or {media.media.title.userPreferred}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
            torrent_search_results: List[Optional[TorrentInfo]] = \
                self.nyaa_controller.search_for_show(show, media, self.app_config)
            if torrent_search_results.__len__() > 0:
                torrent_search_result_list += torrent_search_results
        return torrent_search_result_list

    def download_pending_torrent_files(self, search_results: Optional[List[TorrentInfo]]) -> None:
        """
        Downloads the collected list of torrent into the download directory set in in our app.json
        :param search_results: list of pending items to download
        :return:
        """
        model_helper = NyaaModelHelper()
        if search_results.__len__() > 0:
            for torrent_info in search_results:
                item_exists = self.app_store.search(where('name') == torrent_info.name)
                if item_exists is None or item_exists.__len__() < 1:
                    print()
                    EventLogHelper.log_info(f"Downloading torrent for file -> {torrent_info.name}",
                                            self.__class__.__name__,
                                            inspect.currentframe().f_code.co_name)
                    is_download_successful = self.nyaa_controller.download_torrent_file(torrent_info, self.app_config)
                    if is_download_successful:
                        model_dictionary = model_helper.create_dictionary_class(torrent_info)
                        self.app_store.save_or_update(model_dictionary)
                        print()
                        EventLogHelper.log_info(f"Download successful, anime attributes -> {torrent_info.anime_info}",
                                                self.__class__.__name__,
                                                inspect.currentframe().f_code.co_name)
                    else:
                        print()
                        EventLogHelper.log_info(f"Failed to download, anime attributes -> {torrent_info.anime_info}",
                                                self.__class__.__name__,
                                                inspect.currentframe().f_code.co_name)
                else:
                    print()
                    EventLogHelper.log_info(f"Skipping existing download -> {torrent_info.anime_info}",
                                            self.__class__.__name__,
                                            inspect.currentframe().f_code.co_name)
        else:
            print()
            EventLogHelper.log_info(f"No new episodes to download, ending execution of script",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
        if queued_downloads.__len__() > 0:
            model_helper = NyaaModelHelper()
            for item in queued_downloads:
                StorageUtil.copy_or_move_file(item.name, self.app_config)
                model = model_helper.create_dictionary_class(item)
                self.app_store.save_or_update(model)

    def queue_downloaded_torrent_files(self):
        """
        Copies/moves the torrent files to the desired destination directory specified in the configuration file,
        and uses file watcher to check if the queued extension has been applied to the files before.
        :return:
        """
        pass

    def start_application(self) -> None:
        """
        Application starting point
        :return:
        """
        try:
            anime_list: List[Optional[MediaEntry]] = self.fetch_anime_list()
            print('-------------------------------------------------------')
            if anime_list:
                shows: List[Optional[Show]] = self.find_plex_show(anime_list)
                print('-------------------------------------------------------')
                if shows:
                    missing_shows: Tuple[List[Optional[Show]], List[Optional[MediaEntry]]] \
                        = self.find_missing_show_entries(shows, anime_list)
                    print('-------------------------------------------------------')
                    search_results = self.search_nyaa_for_shows(missing_shows)
                    self.download_pending_torrent_files(search_results)
                    print('-------------------------------------------------------')
        except Exception as e:
            EventLogHelper.log_error(f"Uncaught exception thrown -> {e}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name)
