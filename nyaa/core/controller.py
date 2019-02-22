import inspect
from typing import Optional, List, Dict, Tuple

from NyaaPy import Nyaa
from anitopy import anitopy
from dacite import from_dict
from requests import get, Response

from anilist import MediaTitle, MediaEntry
from app import StorageUtil, EventLogHelper
from plex import Show, Season
from ..data import TorrentWrapper, TorrentInfo, TorrentAnimeInfo, AppConfig


class NyaaControllerHelper:
    """
    Helper class for Nyaa Controller
    """

    @staticmethod
    def _parse_torrent_anime_info(torrent_info: TorrentInfo) -> bool:
        """
        Parse the torrent info name to extract additional information, return true if successful
        otherwise false if the release is a Batch
        :param torrent_info:
        :return:
        """
        parsed_file_name = anitopy.parse(torrent_info.name)
        if parsed_file_name.__contains__('release_information') and parsed_file_name['release_information'] == 'Batch':
            print()
            EventLogHelper.log_info(f"Skipping anime for torrent : {torrent_info.name}\n"
                                    f"details -> {parsed_file_name}",
                                    __name__,
                                    inspect.currentframe().f_code.co_name)
            print('<------------------------------------------------------------>')
            return False
        else:
            torrent_name_info = from_dict(TorrentAnimeInfo, parsed_file_name)
            torrent_info.add_anime_info(torrent_name_info)
            return True

    @staticmethod
    def _build_search_term(media_entry: MediaEntry, config: AppConfig) -> str:
        """
        Builds a search term which will match the kind of release group and quality we're looking for,
        see the app.json file for more details regarding configuration
        :param media_entry:
        :param config:
        :return:
        """
        media_title: MediaTitle = media_entry.media.title
        search_title: str = media_title.romaji
        if search_title is None:
            search_title = media_title.english
        search_term: str = f"{config.torrent_preferred_group} {search_title} {config.torrent_preferred_quality}"
        EventLogHelper.log_info(f"Building search term to use in nyaa.si -> {search_term}",
                                __name__,
                                inspect.currentframe().f_code.co_name)
        return search_term

    @staticmethod
    def __has_seasonal_information(show: Optional[Show], anime_info: TorrentAnimeInfo) -> Tuple[bool, Optional[Season]]:
        if show is not None:
            show_seasons: List[Optional[Season]] = show.seasons()
            for season_item in show_seasons:
                is_finished_watching: bool = season_item.isWatched
                if show_seasons.__len__() < 2:
                    is_finished_watching = False
                """Do some magic here :')"""
                if is_finished_watching is False:
                    return anime_info.has_season_information(), season_item
        return False, None

    @staticmethod
    def __add_to_download_queue(media_entry: MediaEntry, torrent_matches: List[Optional[TorrentInfo]],
                                anime_info: TorrentAnimeInfo, search_result: TorrentInfo):
        if media_entry.has_user_watched_episode(anime_info.episode_number):
            if media_entry.can_add_to_queue(anime_info.episode_number):
                torrent_matches.append(search_result)
                EventLogHelper.log_info(f"Added torrent to download queue -> {search_result.name}",
                                        __name__,
                                        inspect.currentframe().f_code.co_name)

    def _find_matching_episodes(self, show: Optional[Show], media_entry: MediaEntry,
                                search_results: Optional[List[TorrentInfo]]) -> List[Optional[TorrentInfo]]:
        """
        Search for matching required series episodes that need to be downloaded
        :param show:
        :param media_entry:
        :param search_results: a list of torrent information matching the search query
        :return: list of optional torrent info data classes
        """
        torrent_matches: List[Optional[TorrentInfo]] = list()

        for search_result in search_results:
            if not self._parse_torrent_anime_info(search_result):
                continue
            """temporary variable so we don't have to go down the hierarchy structure every time"""
            anime_info = search_result.anime_info
            if media_entry.has_user_watched_episode(anime_info.episode_number):
                has_seasonal_info, season_item = self.__has_seasonal_information(show, anime_info)
                if has_seasonal_info and season_item is not None:
                    if anime_info.has_season_information() and anime_info.season_number == season_item.seasonNumber:
                        self.__add_to_download_queue(media_entry, torrent_matches, anime_info, search_result)
                else:
                    self.__add_to_download_queue(media_entry, torrent_matches, anime_info, search_result)
            else:
                print()
                EventLogHelper.log_info(f"Skipping anime for torrent : {search_result.name}\n"
                                        f"Watch Progress -> {media_entry.progress} | "
                                        f"Episode Number -> {anime_info.episode_number}",
                                        __name__,
                                        inspect.currentframe().f_code.co_name)
                print('<------------------------------------------------------------>')
                break
        return torrent_matches

    @staticmethod
    def _parse_format(search_results: List[Optional[Dict]]) -> TorrentWrapper:
        """
        Creates a data class for the torrent results
        :param search_results:
        :return: a wrapper object containing a list of data class objects
        """
        dictionary_list: dict = dict()
        dictionary_list['response'] = search_results
        return from_dict(TorrentWrapper, dictionary_list)


class NyaaController(NyaaControllerHelper):

    # noinspection PyTypeChecker,PyCallByClass
    def search_for_show(self, show: Optional[Show], media_entry: MediaEntry, config: AppConfig) -> \
            List[Optional[TorrentInfo]]:
        """
        Search for a torrent or torrents using the configuration for release groups and quality
        :param show: plex show item which has information about episodes & seasons
        :param media_entry: anilist it user media entry containing media information and user progress, status & score
        :param config: configuration file from app.json parsed as a data class
        :return: list of optional torrent info data classes
        """
        search_term = self._build_search_term(media_entry, config)
        search_results = Nyaa.search(keyword=search_term, category='1')
        torrent_wrapper = self._parse_format(search_results)
        torrent_results: Optional[List[TorrentInfo]] = torrent_wrapper.response
        return self._find_matching_episodes(show, media_entry, torrent_results)

    # noinspection PyTypeChecker,PyCallByClass
    def get_torrent_details(self, torrent_info: TorrentInfo) -> Optional[TorrentInfo]:
        """
        Gets details about a given torrent
        :param torrent_info: torrent item from search results
        :return: details about the torrent
        """
        torrent_item = Nyaa.get(id=torrent_info.id)
        torrent_wrapper = self._parse_format(f"[{torrent_item}]")
        torrent_info: Optional[TorrentInfo] = torrent_wrapper.response[0]
        self._parse_torrent_anime_info(torrent_info)
        return torrent_info

    @staticmethod
    def download_torrent_file(torrent_info: TorrentInfo, config: AppConfig) -> bool:
        """
        Downloads a .torrent file and saves it into the app/torrents/ directory
        :param config: configuration class
        :param torrent_info:
        :return: True if the operation was successful otherwise False
        """
        torrent_file_name = f"{torrent_info.anime_info.file_name}.torrent"
        response: Response = get(torrent_info.download_url, stream=True)
        StorageUtil.write_file_in_app(directory_path=config.torrent_download_directory,
                                      filename=torrent_file_name, contents=response, write_mode='wb')
        return True
