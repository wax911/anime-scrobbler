from typing import Optional, List, Dict

from NyaaPy import Nyaa
from anitopy import anitopy
from dacite import from_dict
from requests import get, Response

from anilist import MediaTitle, MediaEntry, AiringSchedule
from app import StorageUtil
from plex import Show, Season
from ..data import TorrentWrapper, TorrentInfo, TorrentNameInfo, AppConfig


# noinspection PyTypeChecker,PyCallByClass
class NyaaController:

    def __init__(self) -> None:
        super().__init__()

    @staticmethod
    def __parse_torrent_anime_info(torrent_info: TorrentInfo) -> None:
        parsed_file_name = anitopy.parse(torrent_info.name)
        torrent_name_info = from_dict(TorrentNameInfo, parsed_file_name)
        torrent_info.add_anime_info(torrent_name_info)

    @staticmethod
    def __build_search_term(media_entry: MediaEntry, config: AppConfig) -> str:
        """

        :param media_entry:
        :param config:
        :return:
        """
        media_title: MediaTitle = media_entry.media.title
        search_title: str = media_title.romaji
        if search_title is None:
            search_title = media_title.english
        search_term: str = f"{config.torrent_preferred_group} {search_title} {config.torrent_preferred_quality}"
        return search_term

    @staticmethod
    def __find_matching_episodes(show: Show, media_entry: MediaEntry,
                                 search_results: Optional[List[TorrentInfo]]) -> List[Optional[TorrentInfo]]:
        """
        Search for matching required series episodes that need to be downloaded
        :param show:
        :param media_entry:
        :param search_results: a list of torrent information matching the search query
        :return: list of optional torrent info data classes
        """
        torrent_matches: List[Optional[TorrentInfo]] = list()

        media_entry_progress: int = media_entry.progress
        media_entry_maximum: Optional[int] = media_entry.media.episodes

        media_next_airing: Optional[AiringSchedule] = media_entry.media.nextAiringEpisode
        if media_next_airing is not None:
            media_entry_maximum = media_next_airing.episode

        for torrent_result in search_results:
            NyaaController.__parse_torrent_anime_info(torrent_result)
            """temporary variable so we don't have to go down the hierarchy structure every time"""
            anime_info = torrent_result.anime_info
            if media_entry_progress < int(anime_info.episode_number):
                show_seasons: List[Optional[Season]] = show.seasons()
                for season_item in show_seasons:
                    is_finished_watching: bool = season_item.isWatched
                    if show_seasons.__len__() < 2:
                        is_finished_watching = False
                    """Do some magic here :')"""
                    if is_finished_watching is False:
                        if anime_info.has_season_information():
                            if anime_info.season_number == season_item.seasonNumber:
                                if media_entry_progress < int(anime_info.episode_number):
                                    if int(anime_info.episode_number) < media_entry_maximum:
                                        torrent_matches.append(torrent_result)
                        else:
                            if media_entry_progress < int(anime_info.episode_number):
                                if int(anime_info.episode_number) <= media_entry_maximum:
                                    torrent_matches.append(torrent_result)
            else:
                break
        return torrent_matches

    def search_for_show(self, show: Show, media_entry: MediaEntry, config: AppConfig) -> List[Optional[TorrentInfo]]:
        """
        Search for a torrent or torrents using the configuration for release groups and quality
        :param show: plex show item which has information about episodes & seasons
        :param media_entry: anilist it user media entry containing media information and user progress, status & score
        :param config: configuration file from app.json parsed as a data class
        :return: list of optional torrent info data classes
        """
        search_term = NyaaController.__build_search_term(media_entry, config)
        search_results = Nyaa.search(keyword=search_term, category='1')
        torrent_wrapper = NyaaController.__parse_format(search_results)
        torrent_results: Optional[List[TorrentInfo]] = torrent_wrapper.response
        return self.__find_matching_episodes(show, media_entry, torrent_results)

    @staticmethod
    def get_torrent_details(torrent_info: TorrentInfo) -> Optional[TorrentInfo]:
        """
        Gets details about a given torrent
        :param torrent_info: torrent item from search results
        :return: details about the torrent
        """
        torrent_item = Nyaa.get(id=torrent_info.id)
        torrent_wrapper = NyaaController.__parse_format(f"[{torrent_item}]")
        torrent_info: Optional[TorrentInfo] = torrent_wrapper.response[0]
        NyaaController.__parse_torrent_anime_info(torrent_info)
        return torrent_info

    @staticmethod
    def __parse_format(search_results: List[Optional[Dict]]) -> TorrentWrapper:
        """
        Creates a data class for the torrent results
        :param search_results:
        :return: a wrapper object containing a list of data class objects
        """
        dictionary_list: dict = dict()
        dictionary_list['response'] = search_results
        return from_dict(TorrentWrapper, dictionary_list)

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
