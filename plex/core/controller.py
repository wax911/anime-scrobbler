import json
import logging
from typing import List, Optional

from plexapi.library import ShowSection
from plexapi.server import PlexServer

from app import StorageUtil, EventLogHelper


class PlexController:

    def __init__(self) -> None:
        super().__init__()
        try:
            auth = json.loads(StorageUtil.read_file("auth", "credentials.json"))
            self.plex = PlexServer(auth["url"], auth["token"])
        except Exception as e:
            EventLogHelper.log_error(f"PlexController -> {e}", logging.CRITICAL)

    def find_all_by_title(self, title: str) -> Optional[List[Optional[ShowSection]]]:
        sections = self.plex.library.sections()
        anime_section: Optional[ShowSection]
        for section in sections:
            EventLogHelper.log_info(f"Section {section.title} ->\n"
                                    f"{section.uuid}")
            if section.title == title:
                anime_section = section
                break
        if anime_section is not None:
            all_shows = anime_section.all()
            return all_shows
        else:
            EventLogHelper.log_warning("PlexController#find_all(self) ->\n"
                                       "Unable to find requested section")
            return None

    def update_show(self, show: Optional[ShowSection]):
        pass
