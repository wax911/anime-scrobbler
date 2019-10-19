import inspect
import json
import logging

from time import sleep

# noinspection PyPackageRequirements
from clutch.core import Client
from app import StorageUtil, EventLogHelper


class TransmissionController:

    def __init__(self) -> None:
        super().__init__()
        try:
            __config = json.loads(
                StorageUtil.read_file('auth', 'credentials.json')
            )
            if __config is not None:
                credentials = __config["transmission"]
                self.client = Client(
                    host=credentials["host"],
                    port=credentials["port"],
                    username=credentials["username"],
                    password=credentials["password"]
                )
            else:
                self.client = Client()
        except Exception as e:
            EventLogHelper.log_error(
                f"Encountered exception while initializing controller -> {e}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name,
                logging.CRITICAL
            )

    def add_torrent_magnet(self, filename: str) -> bool:
        """
        adds a magnet link instead of the actual torrent file contents
        :param filename: like of where the file can be found or path to actual file
        :return: True if the operation was a success otherwise False
        """
        try:
            torrent = self.client.torrent.add(filename=filename)
            sleep(.5)
            EventLogHelper.log_info(
                f"Added torrent file url to torrent client -> {torrent} | {filename}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name
            )
            return True
        except Exception as e:
            EventLogHelper.log_warning(
                f"Unable to add torrent to transmission -> {e}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name
            )
            return False

    def add_torrent(self, file_path: str, file_name: str):
        """
        adds the torrent from an existing file path
        :param file_name: name of the file
        :param file_path: where the file can be found
        :return: True if the operation was a success otherwise False
        """
        try:
            file_contents = StorageUtil.read_file(file_path, file_name)
            torrent = self.client.torrent.add(metainfo=file_contents)
            sleep(1.5)
            EventLogHelper.log_info(
                f"Added torrent file to download client -> {torrent} | {file_path}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name
            )
            return True
        except Exception as e:
            EventLogHelper.log_warning(
                f"Unable to add torrent to transmission -> {e}",
                self.__class__.__name__,
                inspect.currentframe().f_code.co_name
            )
            return False
