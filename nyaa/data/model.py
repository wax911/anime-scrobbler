from dataclasses import dataclass


@dataclass()
class NyaaResult:
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

