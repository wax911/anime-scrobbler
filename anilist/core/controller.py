import inspect
import logging

from typing import Optional, Dict, List
from graphql.language.ast import Document

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from app import StorageUtil, EventLogHelper
from ..data import AniListStore, AniListModelHelper, MediaEntry


class AniListController:
    __request_url = 'https://graphql.anilist.co'

    def __init__(self) -> None:
        super().__init__()
        self.model_helper: AniListModelHelper = AniListModelHelper()
        transport = RequestsHTTPTransport(url=self.__request_url)
        self.client = Client(retries=3, transport=transport, fetch_schema_from_transport=True)

    @staticmethod
    def __create_request() -> Document:
        contents = StorageUtil.read_file('query', 'media_collection.graphql')
        return gql(contents)

    def make_request(self, anilist_store: AniListStore):
        request = self.__create_request()
        params = StorageUtil.read_file('config', 'anilist.json')
        response = self.client.execute(request, variable_values=params)
        self.__handle_response(response["MediaListCollection"]["lists"], anilist_store)

    def __handle_response(self, media_collection_list: Optional[List[Dict]], anilist_store: AniListStore):
        try:
            for item in media_collection_list:
                for entry in item['entries']:
                    anilist_store.save_or_update(entry)
        except Exception as e:
            EventLogHelper.log_error(f"Error handling response -> {e}",
                                     self.__class__.__name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)
