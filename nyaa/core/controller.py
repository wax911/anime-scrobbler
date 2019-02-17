from requests import get, Response
from typing import Optional, List
from NyaaPy import Nyaa
from anilist import MediaTitle

from dacite import from_dict

from ..data import TorrentWrapper, TorrentInfo
from app import StorageUtil, EventLogHelper


class NyaaController:

    @staticmethod
    def search_for_show(title: MediaTitle) -> Optional[List[TorrentInfo]]:
        search_title: str = title.romaji
        if search_title is None:
            search_title = title.english
        # noinspection PyTypeChecker,PyCallByClass
        search_results = Nyaa.search(keyword=search_title, category='1_1')
        torrent_wrapper = NyaaController.__parse_format(search_results)
        return torrent_wrapper.response

    @staticmethod
    def __parse_format(search_results: dict) -> TorrentWrapper:
        dictionary_list = dict('response')
        dictionary_list['response'] = search_results
        return from_dict(TorrentWrapper, dictionary_list)

    @staticmethod
    def download_torrent_file(torrent_info: TorrentInfo):
        """
        Downloads a .torrent file and saves it into the app/torrents/ directory
        :param torrent_info:
        :return:
        """
        StorageUtil.read_file('config', 'app.json')
        response: Response = get(torrent_info.url)
        StorageUtil.write_file(src_path='', directory_path='', filename=torrent_info.name,
                               contents=response, write_mode='wb')
