from typing import Optional, List
from NyaaPy import Nyaa
from anilist import MediaTitle


class NyaaController:

    @staticmethod
    def search_for_show(title: MediaTitle) -> Optional[List[dict]]:
        search_title: str = title.romaji
        if search_title is None:
            search_title = title.english
        # noinspection PyTypeChecker,PyCallByClass
        search_results = Nyaa.search(keyword=search_title, category=1)
        return search_results

    @staticmethod
    def download_torrent_file(url: str):
        pass
