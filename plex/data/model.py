from dataclasses import dataclass
from typing import List

from plexapi.video import Show


@dataclass()
class SearchResult:
    search_results: List[Show]
    search_match_term: str
