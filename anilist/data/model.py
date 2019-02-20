from dataclasses import dataclass
from typing import Optional, List


@dataclass()
class AiringSchedule:
    id: int
    airingAt: int
    timeUntilAiring: int
    episode: int


@dataclass()
class FuzzyDate:
    year: Optional[int]
    month: Optional[int]
    day: Optional[int]


@dataclass()
class MediaTitle:
    english: Optional[str]
    romaji: Optional[str]
    native: Optional[str]
    userPreferred: Optional[str]


@dataclass()
class MediaCoverImage:
    large: str
    medium: str


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
    nextAiringEpisode: Optional[AiringSchedule]


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
        Checks if the user has watched the given episode
        :return: true if the user has watched it, otherwise false
        """
        return self.progress < int(episode_number)

    def can_add_to_queue(self, episode_number: str) -> bool:
        """
        Checks if the total/maximum number of episodes are less than or equal to the backlog
        :return: true if this item can be queued, otherwise false
        """
        return int(episode_number) <= self.get_episode_backlog()


@dataclass
class MediaListGroup:
    entries: List[MediaEntry]
    name: str
    isCustomList: bool
    isSplitCompletedList: bool
    status: str
