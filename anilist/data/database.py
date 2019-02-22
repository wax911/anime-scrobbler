import inspect
import logging

from typing import Optional, List, Dict, Any
from tinydb import TinyDB, Query, where
from tinydb.database import Document, Table

from app import EventLogHelper, StorageUtil
from .model import MediaEntry, AniListModelHelper

ANILIST_DATABASE = 'database/anilist.db'


class AniListStore:

    def __init__(self) -> None:
        super().__init__()
        src = StorageUtil.create_base_path(ANILIST_DATABASE)
        self.model_helper = AniListModelHelper()
        self.db: Table = TinyDB(src)

    def save_or_update(self, value: Optional[Dict]):
        result_ids: List[Any] = self.db.upsert(value, where('id') == value['id'])
        if result_ids.__len__() < 1:
            EventLogHelper.log_error(f"Error objects to {ANILIST_DATABASE}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)

    def search(self, query: Query) -> List[Optional[MediaEntry]]:
        query_results: List[Optional[MediaEntry]] = list()
        documents: List[Document] = self.db.search(query)
        try:
            for document in documents:
                data_class = self.model_helper.create_data_class(document)
                query_results.append(data_class)
        except Exception as e:
            EventLogHelper.log_error(f"Database value is not in a valid format {ANILIST_DATABASE}\n"
                                     f"Details: {e}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)
        return query_results

    def get_all(self) -> List[Optional[MediaEntry]]:
        query_results: List[Optional[MediaEntry]] = list()
        documents: List[Document] = self.db.all()
        try:
            for document in documents:
                data_class = self.model_helper.create_data_class(document)
                query_results.append(data_class)
        except Exception as e:
            EventLogHelper.log_error(f"Database value is not in a valid format {ANILIST_DATABASE}\n"
                                     f"Details: {e}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)
        return query_results
