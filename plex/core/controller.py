import inspect
import json
import logging
from typing import List, Optional

from plexapi.library import ShowSection
from plexapi.server import PlexServer
from plexapi.video import Show

from anilist import MediaTitle
from app import StorageUtil, EventLogHelper


class PlexController:

    def __init__(self) -> None:
        super().__init__()
        try:
            self.config = json.loads(StorageUtil.read_file('config', 'plex.json'))
            auth = json.loads(StorageUtil.read_file("auth", "credentials.json"))
            self.plex = PlexServer(auth["url"], auth["token"])
        except Exception as e:
            EventLogHelper.log_error(f"Encountered exception while initializing controller -> {e}",
                                     __name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)

    def find_all_by_title(self, media_title: MediaTitle) -> List[Optional[Show]]:
        """
        Search for plex shows within a configuration given library name
        :param media_title: anime title to search for
        :return: list of optional shows
        """
        all_shows = list()
        try:
            anime_section: Optional[ShowSection] = self.plex.library.section(self.config['section_library_name'])
            if anime_section is not None:
                search_term: str = media_title.english
                if search_term is None:
                    search_term = media_title.romaji
                EventLogHelper.log_info(f"Searching plex for -> {search_term}",
                                        __name__,
                                        inspect.currentframe().f_code.co_name)
                for show in anime_section.search(title=search_term):
                    all_shows.append(show)
            else:
                EventLogHelper.log_warning(f"Unable to find show title-> {media_title.userPreferred} | "
                                           f"{self.config['section_library_name']}",
                                           __name__,
                                           inspect.currentframe().f_code.co_name)
        except Exception as e:
            EventLogHelper.log_info(f"{e}",
                                    __name__,
                                    inspect.currentframe().f_code.co_name)
        finally:
            return all_shows

    def get_seasons_for_show(self, show: Optional[Show]):
        pass

    def update_show(self, show: Optional[ShowSection]):
        pass
