import logging
from typing import Optional
from gql import Client, gql
from gql.transport.requests import RequestsHTTPTransport
from graphql.language.ast import Document

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
        params = '''
        {
            "userId": 80546,
            "userName": "wax911",
            "type": "ANIME",
            "statusIn": ["CURRENT","PLANNING","COMPLETED","PAUSED","DROPPED","REPEATING"],
            "forceSingleCompletedList": true,
            "sort": "MEDIA_ID"
        }
        '''
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
            EventLogHelper.log_error(f"__handle_response(response: Optional[dict]):\n"
                                     f"Exception -> {e}", logging.CRITICAL)
