from re import match, IGNORECASE
from dataclasses import dataclass
from typing import Optional, List


@dataclass()
class AppConfig:
    torrent_monitor_directory: str
    torrent_download_directory: str
    torrent_preferred_quality: str
    torrent_preferred_group: str
    torrent_queued_postfix: str
    torrent_keep_file_after_queuing: bool


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

    def add_anime_info(self, torrent_name_info: TorrentAnimeInfo) -> None:
        """
        Added anime info for the the current torrent
        :param torrent_name_info:
        :return:
        """
        self.anime_info = torrent_name_info


@dataclass()
class TorrentWrapper:
    response: Optional[List[TorrentInfo]]
