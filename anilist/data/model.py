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


@dataclass
class MediaListGroup:
    entries: List[MediaEntry]
    name: str
    isCustomList: bool
    isSplitCompletedList: bool
    status: str
