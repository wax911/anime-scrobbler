import inspect
import logging

import pickledb
from typing import Optional
from dacite import from_dict

from app import EventLogHelper, StorageUtil
from .model import MediaListGroup


ANILIST_DATABASE = 'database/anilist.db'


class PickleStore:

    def __init__(self) -> None:
        super().__init__()
        src = StorageUtil.create_base_path(ANILIST_DATABASE)
        self.db = pickledb.load(location=src, auto_dump=True)

    def save(self, key: str, value: dict):
        result = self.db.set(key, value)
        if not result:
            EventLogHelper.log_error(f"Error saving {key} to {ANILIST_DATABASE}",
                                     __name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)

    def get(self, key: str) -> Optional[MediaListGroup]:
        data_dict = self.db.get(key)
        if isinstance(data_dict, dict):
            return from_dict(data_class=MediaListGroup, data=data_dict)
        else:
            print(data_dict)
        return None

    def exists(self, key: str) -> bool:
        return self.db.exists(key)
