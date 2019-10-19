import inspect
import json
import logging
from difflib import SequenceMatcher
from typing import List, Optional
from unidecode import unidecode
from plexapi.library import ShowSection
from plexapi.server import PlexServer
from plexapi.video import Show

from anilist import MediaEntry
from app import StorageUtil, EventLogHelper

from ..data import SearchResult


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

    def find_all_by_title(self, media_entry: MediaEntry, add_missing) -> List[Optional[Show]]:
        """
        Search for plex shows within a configuration given library name
        :param add_missing:
        :param media_entry: media to look for
        :return: list of optional shows
        """
        all_shows = list()
        try:
            anime_section: Optional[ShowSection] = self.plex.library.section(self.config['section_library_name'])
            if anime_section is not None:
                search_result: SearchResult = self.__search_for_shows(anime_section, media_entry)
                if search_result.search_results:
                    for show in search_result.search_results:
                        show_episodes_count = show.episodes().__len__()
                        episodes = media_entry.media.episodes
                        if show_episodes_count >= episodes:
                            continue
                        all_shows.append(show)
                else:
                    print()
                    search_term = media_entry.media.title.userPreferred
                    EventLogHelper.log_warning(
                        f"Search term not found `{search_term}`, adding to missing shows list",
                        self.__class__.__name__,
                        inspect.currentframe().f_code.co_name
                    )
                    print()
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

    @staticmethod
    def __matches_search_term(show_title: Optional[str], search_term: Optional[str]) -> bool:
        if show_title and search_term:
            show_title_uni = unidecode(show_title).lower()
            search_term_uni = unidecode(search_term).lower()
            match_ratio = SequenceMatcher(a=show_title_uni, b=search_term_uni).ratio()
            return match_ratio >= .98
        return False

    @staticmethod
    def __search_for_shows(anime_section: ShowSection, media_entry: MediaEntry) -> SearchResult:
        search_results: List[Show] = list()
        search_match_term_match: str = ""

        search_terms: List[str] = media_entry.generate_search_terms()

        for search_term in search_terms:
            search_results = anime_section.search(title=search_term)
            if search_results:
                search_match_term_match = search_term
                break

        filtered_search_results: List[Show] = list(
            filter(
                lambda show: PlexController.__matches_search_term(
                    show.title, search_match_term_match
                ), search_results)
        )

        if filtered_search_results:
            EventLogHelper.log_info(
                f"Search term match found `{search_match_term_match}` -> `{filtered_search_results}`",
                "PlexController",
                inspect.currentframe().f_code.co_name
            )

        return SearchResult(
            filtered_search_results,
            search_match_term_match
        )
