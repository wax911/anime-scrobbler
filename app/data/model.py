from dataclasses import dataclass
from typing import List


@dataclass()
class AppState:
    is_queued: bool
    name: str
    size: str
    url: str


@dataclass()
class AppStateWrapper:
    data: List[AppState]
    last_execution_time: int
