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
            EventLogHelper.log_error(f"PlexController -> {e}", logging.CRITICAL)

    def find_all_by_title(self, media_title: MediaTitle) -> List[Optional[Show]]:
        all_shows = list()
        try:
            anime_section: Optional[ShowSection] = self.plex.library.section(self.config['section_library_name'])
            EventLogHelper.log_info(f"Using Section:\n"
                                    f"{anime_section.title} -> {anime_section.uuid}")
            if anime_section is not None:
                search_term: str = media_title.english
                if search_term is None:
                    search_term = media_title.romaji
                for show in anime_section.search(title=search_term):
                    all_shows.append(show)
            else:
                EventLogHelper.log_warning("PlexController#find_all(self) ->\n"
                                           "Unable to find requested section")
        except Exception as e:
            EventLogHelper.log_error(f"PlexController#find_all(self) ->\n"
                                     f"{e}")
        finally:
            return all_shows

    def get_seasons_for_show(self, show: Optional[Show]):
        pass

    def update_show(self, show: Optional[ShowSection]):
        pass
