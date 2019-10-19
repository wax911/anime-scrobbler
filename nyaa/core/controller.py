import inspect
import logging
from time import sleep
from typing import Optional, List, Tuple, Dict

from NyaaPy import Nyaa
from requests import get, Response

from anilist import MediaEntry
from app import StorageUtil, EventLogHelper
from plex import Show, Season
from ..data import NyaaModelHelper, TorrentInfo, TorrentAnimeInfo, AppConfig


class NyaaControllerHelper:
    """
    Helper class for Nyaa Controller
    """

    def __init__(self) -> None:
        super().__init__()
        self.sleep_duration: float = .25
        self.model_helper = NyaaModelHelper()
        self.config: Optional[AppConfig] = None

    @staticmethod
    def _build_search_terms(config: Optional[AppConfig], media_entry: MediaEntry) -> List[str]:
        """
        Builds a search term which will match the kind of release group and quality we're looking for,
        see the app.json file for more details regarding configuration
        :param media_entry:
        :return:
        """
        search_terms: List[str] = list(map(
            lambda s: f"{config.torrent_preferred_group} {s} {config.torrent_preferred_quality}",
            media_entry.generate_search_terms()
        ))
        return search_terms

    @staticmethod
    def __has_seasonal_information(show: Optional[Show], anime_info: TorrentAnimeInfo) -> Tuple[bool, Optional[Season]]:
        if show is not None:
            show_seasons: List[Optional[Season]] = show.seasons()
            for season_item in show_seasons:
                is_finished_watching: bool = season_item.isWatched
                if len(show_seasons) < 2:
                    is_finished_watching = False
                """Do some magic here :')"""
                if not is_finished_watching:
                    return anime_info.has_season_information(), season_item
        return False, None

    def _find_missing_episodes(
            self,
            show: Optional[Show],
            search_results: Optional[List[TorrentInfo]]
    ) -> List[Optional[TorrentInfo]]:
        """
        Find episodes that might not exist and add then to the download queue
        :return:
        """
        torrent_matches: List[Optional[TorrentInfo]] = list()

        for search_result in search_results:
            sleep(self.sleep_duration)
            if not search_result.added_anime_info():
                continue

            anime_info = search_result.anime_info
            if f"[{anime_info.release_group}]" != self.config.torrent_preferred_group:
                continue

            is_episode_present = False
            for episode in show.episodes():
                is_episode_present = episode.index == int(float(anime_info.episode_number))
                if is_episode_present:
                    break

            if not is_episode_present:
                EventLogHelper.log_info(
                    f"Adding missing episode: `{anime_info.file_name}`",
                    self.__class__.__name__,
                    inspect.currentframe().f_code.co_name
                )
                torrent_matches.append(search_result)

        return torrent_matches


class NyaaController(NyaaControllerHelper):

    @staticmethod
    def __search_for_matching_until_found(search_page: int, search_terms: List[str]):
        for search_term in search_terms:
            # noinspection PyTypeChecker,PyCallByClass
            search_results = Nyaa.search(keyword=search_term, category='1', page=search_page)
            if search_results:
                EventLogHelper.log_info(
                    f"Nyaa search results found for search term: {search_term} | page: {search_page}"
                    f" | found `{search_results.__len__()}` results",
                    "NyaaController",
                    inspect.currentframe().f_code.co_name
                )
                return search_results

    def search_for_shows(
            self,
            show: Optional[Show],
            media_entry: MediaEntry,
            config: AppConfig
    ) -> List[Optional[TorrentInfo]]:
        """
        Search for a torrent or torrents using the configuration for release groups and quality
        :param show: plex show item which has information about episodes & seasons
        :param media_entry: anilist users media entry containing media information and user progress, status & score
        :param config: configuration file from app.json parsed as a data class
        :return: list of optional torrent info data classes
        """
        has_more_results = True
        search_page: int = 1
        self.config = config
        search_results: List[Dict[Optional[str], Optional[str]]] = list()

        while has_more_results:
            sleep(self.sleep_duration)
            temp_search_results = self.__search_for_matching_until_found(
                search_page, self._build_search_terms(self.config, media_entry)
            )
            if temp_search_results is not None and len(temp_search_results) > 0:
                search_results += temp_search_results
                search_page += 1
            else:
                has_more_results = False

        torrent_info_results: List[Optional[TorrentInfo]] = list()
        for search_result in search_results:
            sleep(self.sleep_duration)
            torrent_info = self.model_helper.create_data_class(search_result)
            if torrent_info is not None:
                torrent_info_results.append(torrent_info)

        # return self._find_matching_episodes(show, media_entry, torrent_info_results)
        return self._find_missing_episodes(show, torrent_info_results)

    def search_for_missing_shows(
            self,
            media_entry: MediaEntry,
            config: AppConfig
    ) -> List[Optional[TorrentInfo]]:
        """
        Search for a torrent or torrents using the configuration for release groups and quality
        :param media_entry: anilist users media entry containing media information and user progress, status & score
        :param config: configuration file from app.json parsed as a data class
        :return: list of optional torrent info data classes
        """
        has_more_results = True
        search_page: int = 1
        self.config = config
        search_results: List[Dict[Optional[str], Optional[str]]] = list()

        while has_more_results:
            sleep(self.sleep_duration)
            temp_search_results = self.__search_for_matching_until_found(
                search_page, self._build_search_terms(self.config, media_entry)
            )
            if temp_search_results is not None and len(temp_search_results) > 0:
                search_results += temp_search_results
                search_page += 1
            else:
                has_more_results = False

        torrent_info_results: List[Optional[TorrentInfo]] = list()
        for search_result in search_results:
            sleep(self.sleep_duration)
            torrent_info = self.model_helper.create_data_class(search_result)
            if torrent_info is not None:
                torrent_info_results.append(torrent_info)

        return torrent_info_results

    @staticmethod
    def download_torrent_file(torrent_info: TorrentInfo, config: AppConfig) -> bool:
        """
        Downloads a .torrent file and saves it into the app/torrents/ directory
        :param config: configuration class
        :param torrent_info:
        :return: True if the operation was successful otherwise False
        """
        try:
            print()
            torrent_file_name = f"{torrent_info.anime_info.file_name}.torrent"
            response: Response = get(
                url=torrent_info.download_url,
                allow_redirects=True,
                stream=True,
                timeout=30.0
            )

            if response.ok:
                StorageUtil.write_file_in_app(
                    directory_path=config.build_parent_save_path(
                        torrent_info.anime_info.anime_title
                    ),
                    filename=torrent_file_name,
                    contents=response,
                    write_mode='wb'
                )
            else:
                EventLogHelper.log_info(
                    f"Requesting torrent for download failed : {response}\n"
                    f"Retrying in 5 seconds..",
                    "NyaaController",
                    inspect.currentframe().f_code.co_name
                )
                sleep(5)
                NyaaController.download_torrent_file(torrent_info, config)
            print('<------------------------------------------------------------>')
        except Exception as e:
            EventLogHelper.log_error(
                f"Encountered exception while downloading torrent file -> {e}",
                "NyaaController",
                inspect.currentframe().f_code.co_name,
                logging.CRITICAL
            )
            return False
        return True
