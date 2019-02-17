import pickledb
from typing import Optional
from dacite import from_dict

from app import EventLogHelper, StorageUtil
from .model import AppState
from . import APP_DATABASE


class PickleStore:

    def __init__(self) -> None:
        super().__init__()
        src = StorageUtil.create_base_path(APP_DATABASE)
        self.db = pickledb.load(location=src, auto_dump=True)

    def save(self, key: str, value: dict):
        result = self.db.set(key, value)
        if result:
            EventLogHelper.log_info(f"Saved dictionary: \n"
                                    f"Key -> {key}")
        else:
            EventLogHelper.log_info(f"saved dictionary successfully")

    def get(self, key: str) -> Optional[AppState]:
        data_dict = self.db.get(key)
        if data_dict is dict:
            return from_dict(data_class=AppState, data=data_dict)
        else:
            print(data_dict)
        return None

    def exists(self, key: str) -> bool:
        return self.db.exists(key)
