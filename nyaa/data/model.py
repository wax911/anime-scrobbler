from dataclasses import dataclass
from typing import Optional, List


@dataclass()
class TorrentInfo:
    category: str
    url: str
    name: str
    download_url: str
    magnet: str
    size: str
    date: str
    seeders: str
    leechers: str
    completed_downloads: str


@dataclass()
class TorrentWrapper:
    response: Optional[List[TorrentInfo]]
