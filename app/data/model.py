from dataclasses import dataclass


@dataclass()
class AppState:
    is_queued: bool
    name: str
    size: int
    url: str


@dataclass()
class AppConfig:
    torrent_monitor_directory: str
    torrent_download_directory: str
    torrent_preferred_group: str
    torrent_queued_postfix: str
    torrent_file_move_after_download: bool
