import inspect
import logging
from typing import Optional

from graphql.language.ast import Document

from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport

from app import StorageUtil, EventLogHelper
from ..data import PickleStore


class AniListController:
    __request_url = 'https://graphql.anilist.co'

    def __init__(self) -> None:
        super().__init__()
        transport = RequestsHTTPTransport(url=self.__request_url)
        self.client = Client(retries=3, transport=transport, fetch_schema_from_transport=True)

    @staticmethod
    def __create_request() -> Document:
        contents = StorageUtil.read_file('query', 'media_collection.graphql')
        return gql(contents)

    def make_request(self):
        request = self.__create_request()
        params = StorageUtil.read_file('config', 'anilist.json')
        response = self.client.execute(request, variable_values=params)
        self.__handle_response(response)

    @staticmethod
    def __handle_response(response: Optional[dict]):
        try:
            media_lists = response["MediaListCollection"]["lists"]
            pickle_store = PickleStore()
            for entry in media_lists:
                pickle_store.save(entry["status"], entry)
        except Exception as e:
            EventLogHelper.log_error(f"Error handling response -> {e}",
                                     __name__,
                                     inspect.currentframe().f_code.co_name,
                                     logging.CRITICAL)
