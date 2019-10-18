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
            EventLogHelper.log_error(
                f"Encountered exception while initializing controller -> {e}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                logging.CRITICAL
            )

    def find_all_by_title(self, media_title: MediaTitle, episodes: Optional[int], add_missing) -> List[Optional[Show]]:
        """
        Search for plex shows within a configuration given library name
        :param add_missing:
        :param media_title: anime title to search for
        :param episodes: number of available episodes
        :return: list of optional shows
        """
        all_shows = list()
        try:
            anime_section: Optional[ShowSection] = self.plex.library.section(self.config['section_library_name'])
            if anime_section is not None:
                search_term: str = media_title.english
                if search_term is None:
                    search_term = media_title.romaji
                for show in anime_section.search(title=search_term):
                    show_item: Show = show
                    if episodes is not None and show_item.episodes().__len__() >= episodes:
                        continue
                    if show_item.title.lower() != search_term.lower():
                        EventLogHelper.log_info(f"Skipping item mismatch term {show_item.title} != {search_term}",
                                                self.__class__.__name__,
                                                inspect.currentframe().f_code.co_name)
                        continue
                    EventLogHelper.log_info(
                        f"Found `{search_term}` in plex, adding to list of possible downloadable items",
                        self.__class__.__name__,
                        inspect.currentframe().f_code.co_name
                    )
                    all_shows.append(show_item)
            else:
                EventLogHelper.log_warning(
                    f"Unable to find show title-> `{media_title.userPreferred}` | "
                    f"{self.config['section_library_name']} in plex, adding to list of missing shows",
                    __name__,
                    inspect.currentframe().f_code.co_name
                )
                add_missing()
        except Exception as e:
            EventLogHelper.log_info(
                f"{e}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name
            )
        return all_shows

    def get_seasons_for_show(self, show: Optional[Show]):
        pass

    def update_show(self, show: Optional[ShowSection]):
        pass
