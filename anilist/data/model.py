import inspect
from unidecode import unidecode
from dataclasses import dataclass
from typing import Optional, List, Dict

from dacite import from_dict

from app import EventLogHelper


@dataclass()
class AiringSchedule:
    id: int
    airingAt: int
    timeUntilAiring: int
    episode: int

    def __iter__(self):
        yield 'id', self.id
        yield 'airingAt', self.airingAt
        yield 'timeUntilAiring', self.timeUntilAiring
        yield 'episode', self.episode


@dataclass()
class FuzzyDate:
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]

    def __iter__(self):
        yield 'year', self.year
        yield 'month', self.month
        yield 'day', self.day


@dataclass()
class MediaTitle:
    english: Optional[str]
    romaji: Optional[str]
    native: Optional[str]
    userPreferred: Optional[str]

    def __iter__(self):
        yield 'english', self.english
        yield 'romaji', self.romaji
        yield 'native', self.native
        yield 'userPreferred', self.userPreferred


@dataclass()
class MediaCoverImage:
    large: str
    medium: str

    def __iter__(self):
        yield 'large', self.large
        yield 'medium', self.medium


@dataclass()
class Media:
    id: int
    title: MediaTitle
    coverImage: MediaCoverImage
    type: str
    format: str
    season: Optional[str]
    status: str
    meanScore: Optional[int]
    averageScore: Optional[int]
    startDate: Optional[FuzzyDate]
    endDate: Optional[FuzzyDate]
    episodes: Optional[int]
    isAdult: bool
    isFavourite: bool
    synonyms: Optional[List[str]]
    nextAiringEpisode: Optional[AiringSchedule]

    def __iter__(self):
        yield 'id', self.id
        yield 'title', self.title
        yield 'coverImage', self.coverImage
        yield 'type', self.type
        yield 'format', self.format
        yield 'season', self.season
        yield 'status', self.status
        yield 'meanScore', self.meanScore
        yield 'averageScore', self.averageScore
        yield 'startDate', self.startDate
        yield 'endDate', self.endDate
        yield 'episodes', self.episodes
        yield 'isAdult', self.isAdult
        yield 'isFavourite', self.isFavourite
        yield 'synonyms', self.synonyms
        yield 'nextAiringEpisode', self.nextAiringEpisode


@dataclass
class MediaEntry:
    id: int
    mediaId: int
    status: str
    score: int
    progress: int
    priority: int
    private: bool
    hiddenFromStatusLists: bool
    media: Media

    def generate_search_terms(self) -> List[str]:
        """
        Returns a list of possible search terms
        :return:
        """
        search_terms: List[str] = list()
        if self.media.title.english is not None:
            search_terms.append(unidecode(self.media.title.english))
        if self.media.title.romaji is not None and not search_terms.count(self.media.title.romaji):
            search_terms.append(unidecode(self.media.title.romaji))

        for synonym in self.media.synonyms:
            search_terms.append(unidecode(synonym))

        return search_terms

    def get_episode_backlog(self) -> int:
        """
        Checks what the upper bound from the current progress for an anime is,
        in turn this will be translated to the number of episodes the user is behind on
        :return: number of episode the user is behind on
        """
        media_entry_maximum: Optional[int] = self.media.episodes
        media_next_airing: Optional[AiringSchedule] = self.media.nextAiringEpisode
        if media_next_airing is not None:
            media_entry_maximum = media_next_airing.episode
        return media_entry_maximum

    def has_user_watched_episode(self, episode_number: str) -> bool:
        """
        Checks if the episode exists in otherwise checks if the user has watched the given episode
        :return: true if the user has watched it, otherwise false
        """
        return self.progress > int(float(episode_number))

    def can_add_to_queue(self, episode_number: str) -> bool:
        """
        Checks if the total/maximum number of episodes are less than or equal to the backlog
        :return: true if this item can be queued, otherwise false
        """
        return int(float(episode_number)) <= self.get_episode_backlog()

    def __iter__(self):
        yield 'id', self.id
        yield 'mediaId', self.mediaId
        yield 'status', self.status
        yield 'score', self.score
        yield 'progress', self.progress
        yield 'priority', self.priority
        yield 'private', self.private
        yield 'hiddenFromStatusLists', self.hiddenFromStatusLists
        yield 'media', self.media


# @dataclass
# class MediaListGroup:
#     entries: List[MediaEntry]
#     name: str
#     isCustomList: bool
#     isSplitCompletedList: bool
#     status: str


class AniListModelHelper:

    def create_data_class(self, response: Optional[Dict]) -> Optional[MediaEntry]:
        parsed_object: Optional[List[MediaEntry]] = None
        try:
            parsed_object = from_dict(MediaEntry, response)
        except Exception as e:
            print()
            EventLogHelper.log_info(f"Error converting dictionary to data class\n"
                                    f"details -> {e}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
            print('<------------------------------------------------------------>')
        return parsed_object

    def create_dictionary_class(self, response: MediaEntry) -> Optional[Dict]:
        parsed_dictionary: Optional[Dict] = None
        try:
            parsed_dictionary = dict(response)
        except Exception as e:
            print()
            EventLogHelper.log_info(f"Error converting data class to dictionary\n"
                                    f"details -> {e}",
                                    self.__class__.__name__,
                                    inspect.currentframe().f_code.co_name)
            print('<------------------------------------------------------------>')
        return parsed_dictionary
