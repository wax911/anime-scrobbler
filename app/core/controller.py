import inspect
import json

from typing import Optional, List
from dacite import from_dict
from tinydb import where

from anilist import AniListController, MediaEntry, AniListStore
from app import EventLogHelper
from nyaa import NyaaController, TorrentInfo, AppConfig, NyaaModelHelper

from transmission import TransmissionController
from plex import PlexController, Show

from ..data import AppStore, DownloadableQueue
from ..util import StorageUtil


class AppController:

    def __init__(self, list_name: str) -> None:
        super().__init__()
        self.list_name = list_name
        self.anilist_search_query = (where('status') == list_name)

        self.transmission_controller: TransmissionController = TransmissionController()
        self.anilist_controller: AniListController = AniListController()
        self.plex_controller: PlexController = PlexController()
        self.nyaa_controller: NyaaController = NyaaController()

        self.nyaa_model_helper = NyaaModelHelper()
        self.app_store: AppStore = AppStore()
        self.app_config = self.__get_app_configuration()

    @staticmethod
    def __get_app_configuration() -> AppConfig:
        json_string = json.loads(StorageUtil.read_file('config', 'app.json'))
        return from_dict(AppConfig, json_string)

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

    @staticmethod
    def __add_missing_item(media_entry: MediaEntry, append_list: List[Optional[MediaEntry]]):
        append_list.append(media_entry)

    def find_plex_show(self, media_entries: List[MediaEntry]) -> DownloadableQueue:
        """
        Fetches a list of shows by title if they exist, if not an empty collection would be returned
        :param media_entries: a model consisting of various anime names from anilist
        :return: a list of optional shows
        """
        shows_in_plex_matching_users_list: List[Optional[Show]] = list()
        show_media_entry_mapped_to_plex: List[Optional[MediaEntry]] = list()
        shows_missing_in_plex_found_on_users_list: List[Optional[MediaEntry]] = list()
        for entry in media_entries:
            if entry.media.status != 'NOT_YET_RELEASED':
                if entry.status != 'COMPLETED':
                    show = self.plex_controller.find_all_by_title(
                        entry,
                        lambda: self.__add_missing_item(
                            entry,
                            shows_missing_in_plex_found_on_users_list
                        )
                    )
                    if show:
                        shows_in_plex_matching_users_list += show
                        show_media_entry_mapped_to_plex.append(entry)
        EventLogHelper.log_info(
            f"Fetched list of shows by title, returned {shows_in_plex_matching_users_list.__len__()} results.\n"
            f"Items which could not be found in plex {shows_missing_in_plex_found_on_users_list.__len__()}.",
            self.__class__.__name__,
            inspect.currentframe().f_code.co_name
        )
        return DownloadableQueue(
            shows_in_plex_matching_users_list,
            shows_missing_in_plex_found_on_users_list,
            show_media_entry_mapped_to_plex
        )

    def search_nyaa_for_shows(self, download_queue: DownloadableQueue) -> Optional[List[TorrentInfo]]:
        """
        Searches nyaa.si for torrents matching the tittle name/s
        :param download_queue: a model consisting of a tuple shows and media entries of missing episodes
        :return: a list of torrent results
        """
        torrent_search_result_list: List[TorrentInfo] = list()
        torrent_search_result_list_for_missing_shows: List[TorrentInfo] = list()

        print()
        print('-------------------------------------------------------')

        EventLogHelper.log_info(
            f"Searching for missing items in plex",
            self.__class__.__name__,
            inspect.currentframe().f_code.co_name
        )
        for media in download_queue.shows_missing_in_plex:
            torrent_search_results = self.nyaa_controller.search_for_missing_shows(media, self.app_config)
            if torrent_search_results.__len__() > 0:
                torrent_search_result_list_for_missing_shows += torrent_search_results
            else:
                EventLogHelper.log_info(
                    f"Unable to find {media.media.title.userPreferred} from nyaa.si",
                    self.__class__.__name__,
                    inspect.currentframe().f_code.co_name
                )
        print('-------------------------------------------------------')
        print()

        print()
        print('-------------------------------------------------------')
        EventLogHelper.log_info(
            f"Searching for matching items in plex",
            self.__class__.__name__,
            inspect.currentframe().f_code.co_name
        )
        for show, media in zip(download_queue.shows_found_in_plex, download_queue.show_media_entry_in_plex):
            torrent_search_results = self.nyaa_controller.search_for_shows(
                show, media, self.app_config
            )

            if torrent_search_results.__len__() > 0:
                print()
                torrent_search_result_list += torrent_search_results
            else:
                EventLogHelper.log_info(
                    f"No new releases found for the following torrent/s `{media.generate_search_terms()}` on nyaa.si",
                    self.__class__.__name__,
                    inspect.currentframe().f_code.co_name
                )
                print()
        print('-------------------------------------------------------')
        print()
        return torrent_search_result_list + torrent_search_result_list_for_missing_shows

    def __find_downloadable_torrents(self, torrent_info: TorrentInfo) -> List[Optional[TorrentInfo]]:
        return self.app_store.search(where('name') == torrent_info.name)

    @staticmethod
    def __downloads_are_not_empty(torrents: List[Optional[TorrentInfo]]) -> bool:
        return torrents is None or torrents.__len__() < 1

    def __download_torrent_file(self, torrent_info: TorrentInfo):
        print()
        EventLogHelper.log_info(f"Downloading torrent for file -> {torrent_info.name}",
                                self.__class__.__name__,
                                inspect.currentframe().f_code.co_name)
        is_download_successful = self.nyaa_controller.download_torrent_file(torrent_info, self.app_config)
        if is_download_successful:
            model_dictionary = self.nyaa_model_helper.create_dictionary_class(torrent_info)
            self.app_store.save_or_update(model_dictionary)
            print()
            EventLogHelper.log_info(f"Download successful, anime attributes -> {torrent_info.anime_info}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
            self.__move_torrent_to_monitored_directory(torrent_info)
        else:
            print()
            EventLogHelper.log_info(f"Failed to download, anime attributes -> {torrent_info.anime_info}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)

    def __move_torrent_to_monitored_directory(self, torrent_info: TorrentInfo):
        try:
            StorageUtil.copy_or_move_file(
                filename=f"{torrent_info.name}.torrent",
                directory_path=self.app_config.build_parent_save_path(
                    torrent_info.anime_info.anime_title
                ),
                destination_path=self.app_config.torrent_monitor_directory,
                keep_file=self.app_config.torrent_keep_file_after_queuing
            )

            model = self.nyaa_model_helper.create_dictionary_class(torrent_info)
            self.app_store.save_or_update(model)
        except Exception as e:
            EventLogHelper.log_error(
                f"__move_torrent_to_monitored_directory -> StorageUtil.copy_or_move_file -> {e}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name
            )

    def __queue_downloaded_torrent_file(self, torrent_info: TorrentInfo) -> bool:
        """
        Attempts to add the torrent file to the client that handles torrent downloads
        :param torrent_info: torrent item to queue
        :return: True if the operation was a success
        """
        success = self.transmission_controller.add_torrent_magnet(
            filename=torrent_info.download_url
        )

        if success:
            model = self.nyaa_model_helper.create_dictionary_class(torrent_info)
            self.app_store.save_or_update(model)

        return success

    def start_application(self) -> None:
        """
        Application starting point
        :return:
        """
        try:
            anime_list: List[Optional[MediaEntry]] = self.fetch_anime_list()
            print('-------------------------------------------------------')
            if anime_list:
                download_queue: DownloadableQueue = self.find_plex_show(anime_list)
                print('-------------------------------------------------------')
                if download_queue.contains_items():
                    print('-------------------------------------------------------')
                    search_results = self.search_nyaa_for_shows(download_queue)

                    if search_results.__len__() > 0:
                        for torrent_info in search_results:
                            torrents = self.__find_downloadable_torrents(torrent_info)
                            if AppController.__downloads_are_not_empty(torrents):
                                queued: bool = self.__queue_downloaded_torrent_file(torrent_info)
                                if not queued:
                                    self.__download_torrent_file(torrent_info)
                            else:
                                print()
                                EventLogHelper.log_info(f"Skipping existing download -> {torrent_info.anime_info}",
                                                        self.__class__.__name__,
                                                        inspect.currentframe().f_code.co_name)
                    else:
                        print()
                        EventLogHelper.log_info(
                            f"No new episodes to download, ending execution of script",
                            self.__class__.__name__,
                            inspect.currentframe().f_code.co_name
                        )
                    print('-------------------------------------------------------')
        except Exception as e:
            EventLogHelper.log_error(f"Uncaught exception thrown -> {e}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name)
