import inspect
from dataclasses import dataclass
from re import match, IGNORECASE
from typing import Optional, Dict, Union

from anitopy import anitopy
from dacite import from_dict

from app import EventLogHelper


@dataclass()
class AppConfig:
    torrent_monitor_directory: str
    torrent_download_directory: str
    torrent_preferred_quality: str
    torrent_preferred_group: str
    torrent_queued_postfix: str
    torrent_keep_file_after_queuing: bool

    def build_parent_save_path(self, child_directory: str) -> Union[bytes, str]:
        import os
        return os.path.join(self.torrent_download_directory, child_directory)


@dataclass()
class TorrentAnimeInfo:
    file_name: Optional[str]
    file_extension: Optional[str]
    video_resolution: Optional[str]
    episode_number: Optional[str]
    anime_title: Optional[str]
    release_group: Optional[str]
    season_number: Optional[int]

    def has_season_information(self) -> bool:
        """
        Checks if the anime_title has seasonal information
        :return: True if any seasonal information exists otherwise False
        """
        if self.anime_title is not None:
            segments = self.anime_title.split(' ')
            look_up = match(r'([S](\d{1,3}))|(Season.(\d{1,3}))', segments[-1], IGNORECASE)
            if look_up is not None:
                self.season_number = int(look_up.group(1))
                return True
        return False

    def __iter__(self):
        yield 'file_name', self.file_name
        yield 'file_extension', self.file_extension
        yield 'video_resolution', self.video_resolution
        yield 'episode_number', self.episode_number
        yield 'anime_title', self.anime_title
        yield 'release_group', self.release_group
        yield 'season_number', self.season_number


@dataclass()
class TorrentInfo:
    id: Optional[str]
    category: str
    uploader: Optional[str]
    website: Optional[str]
    url: Optional[str]
    name: Optional[str]
    download_url: Optional[str]
    magnet: Optional[str]
    size: str
    date: str
    seeders: str
    leechers: str
    hash: Optional[str]
    anime_info: Optional[TorrentAnimeInfo]
    is_queued: Optional[bool]

    def added_anime_info(self) -> bool:
        """
        Added anime info for the the current torrent
        :return: true if successful otherwise false if the release is a Batch
        """
        parsed_file_name = ""
        try:
            parsed_file_name = anitopy.parse(self.name)
            if not isinstance(parsed_file_name['episode_number'], str) \
                    or parsed_file_name.__contains__('release_information') \
                    and parsed_file_name['release_information'] == 'Batch':
                print()
                EventLogHelper.log_info(f"Skipping anime for torrent : {self.name}\n"
                                        f"details -> {parsed_file_name}",
                                        self.__class__.__name__,
                                        inspect.currentframe().f_code.co_name)
                print('<------------------------------------------------------------>')
                return False
            else:
                torrent_name_info = from_dict(TorrentAnimeInfo, parsed_file_name)
                self.anime_info = torrent_name_info
                return True
        except Exception as e:
            print()
            EventLogHelper.log_info(f"Error converting dictionary to data class\n"
                                    f"details -> {e} | {parsed_file_name}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
            print('<------------------------------------------------------------>')
            return False

    def __iter__(self):
        yield 'id', self.id
        yield 'category', self.category
        yield 'uploader', self.uploader
        yield 'website', self.website
        yield 'url', self.url
        yield 'name', self.name
        yield 'download_url', self.download_url
        yield 'magnet', self.magnet
        yield 'size', self.size
        yield 'date', self.date
        yield 'seeders', self.seeders
        yield 'leechers', self.leechers
        yield 'hash', self.hash
        yield 'anime_info', dict(self.anime_info)
        yield 'is_queued', self.is_queued


# @dataclass()
# class TorrentWrapper:
#     response: Optional[List[TorrentInfo]]


class NyaaModelHelper:

    def __init__(self) -> None:
        super().__init__()

    def create_data_class(self, response: Optional[Dict]) -> Optional[TorrentInfo]:
        parsed_object: Optional[TorrentInfo] = None
        try:
            parsed_object = from_dict(TorrentInfo, response)
        except Exception as e:
            print()
            EventLogHelper.log_info(f"Error converting dictionary to data class\n"
                                    f"details -> {e}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
            print('<------------------------------------------------------------>')
        return parsed_object

    def create_dictionary_class(self, response: Optional[TorrentInfo]) -> Optional[Dict]:
        parsed_dictionary: Optional[Dict] = None
        try:
            parsed_dictionary = dict(response)
        except Exception as e:
            print()
            EventLogHelper.log_info(f"Error converting data class to dictionary\n"
                                    f"details -> {e}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
            print('<------------------------------------------------------------>')
        return parsed_dictionary
