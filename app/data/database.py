import inspect
import logging

from typing import Optional, List, Dict, Any
from tinydb import TinyDB, Query, where
from tinydb.database import Document, Table

from app import EventLogHelper, StorageUtil
from nyaa import TorrentInfo, NyaaModelHelper

APP_DATABASE = 'database/history.db'


class AppStore:

    def __init__(self) -> None:
        super().__init__()
        src = StorageUtil.create_base_path(APP_DATABASE)
        self.model_helper = NyaaModelHelper()
        self.db: TinyDB = TinyDB(src)

    def save_or_update(self, value: Optional[Dict]):
        result_ids: List[Any] = self.db.upsert(value, where('name') == value['name'])
        if result_ids.__len__() < 1:
            EventLogHelper.log_error(f"Error objects to {APP_DATABASE}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)

    def search(self, query: Query) -> List[Optional[TorrentInfo]]:
        query_results: List[Optional[TorrentInfo]] = list()
        documents: List[Document] = self.db.search(query)
        try:
            for document in documents:
                data_class = self.model_helper.create_data_class(document)
                query_results.append(data_class)
        except Exception as e:
            EventLogHelper.log_error(f"Database value is not in a valid format {APP_DATABASE}\n"
                                     f"Details: {e}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)
        return query_results

    def get_all(self) -> List[Optional[TorrentInfo]]:
        query_results: List[Optional[TorrentInfo]] = list()
        documents: List[Document] = self.db.all()
        try:
            for document in documents:
                data_class = self.model_helper.create_data_class(document)
                query_results.append(data_class)
        except Exception as e:
            EventLogHelper.log_error(f"Database value is not in a valid format {APP_DATABASE}\n"
                                     f"Details: {e}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)
        return query_results
