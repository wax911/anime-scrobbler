import inspect
import os
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Optional, Any


class StorageUtil:

    @staticmethod
    def __get_base_dir():
        current_path = os.path.abspath(os.path.dirname(__file__))
        return os.path.join(current_path, '..')

    @staticmethod
    def create_base_path(file_name: str) -> str:
        base_directory = StorageUtil.__get_base_dir
        return os.path.join(base_directory(), file_name)

    @staticmethod
    def get_file_contents(file_name):
        with open(os.path.join(file_name)) as file:
            input_data = json.loads(file.read())
        return input_data

    @staticmethod
    def create_directory(src_path: str, directory_path: str) -> None:
        creation_path = os.path.join(src_path, directory_path)
        if not os.path.exists(creation_path):
            path = Path(creation_path)
            path.mkdir(parents=True, exist_ok=True)

    @staticmethod
    def read_file(directory_path: str, filename: str) -> Optional[str]:
        file_path = os.path.join(StorageUtil.__get_base_dir(), directory_path)
        if os.path.exists(file_path):
            path = Path(file_path)
            with open(os.path.join(path, filename), "r") as reader:
                contents = reader.read()
            return contents
        else:
            EventLogHelper.log_warning(f"File cannot be found file_path -> {file_path}",
                                       __name__,
                                       inspect.currentframe().f_code.co_name)
            return None

    @staticmethod
    def write_file(src_path: str, directory_path: str, filename: str, contents: Any, write_mode='w+') -> None:
        creation_path = os.path.join(src_path, directory_path)
        if not os.path.exists(creation_path):
            path = Path(creation_path)
            path.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(creation_path, filename), write_mode) as writer:
            writer.write(contents)

    @staticmethod
    def write_file_in_app(directory_path: str, filename: str, contents: Any, write_mode='w+') -> None:
        creation_path = os.path.join(StorageUtil.__get_base_dir(), directory_path)
        if not os.path.exists(creation_path):
            path = Path(creation_path)
            path.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(creation_path, filename), write_mode) as writer:
            for chunk in contents.iter_content(chunk_size=256):
                if chunk:
                    writer.write(chunk)

    @staticmethod
    def create_file(directory_path: str, filename: str, contents: Any) -> str:
        if not os.path.exists(directory_path):
            path = Path(directory_path)
            path.mkdir(parents=True, exist_ok=True)
        with open(os.path.join(directory_path, filename), "a+") as writer:
            writer.write(contents)
        return os.path.join(directory_path, filename)


class EventLogHelper:
    LOG_FORMAT = '%(asctime)s | %(levelname)s | %(module)s | %(source)s | %(message)s'
    TIME_FORMAT = '%d/%m/%Y %I:%M:%S %p'

    @staticmethod
    def __get_current_date_time() -> Any:
        return datetime.now().strftime("%d_%b_%y")

    @staticmethod
    def __get_log_file(postfix: str) -> str:
        file_name = f'{EventLogHelper.__get_current_date_time()}.log'
        current_directory = os.path.abspath(os.path.dirname(__file__))
        directory_path = os.path.join(current_directory, '..', 'logs')
        return StorageUtil.create_file(directory_path, file_name, '')

    @staticmethod
    def log_info(message: Any, module_name: str, function_name: str = inspect.currentframe().f_code.co_name):
        logging.basicConfig(filename=EventLogHelper.__get_log_file("INFO"),
                            format=EventLogHelper.LOG_FORMAT,
                            datefmt=EventLogHelper.TIME_FORMAT,
                            level=logging.INFO)
        bundle = {'module_name': module_name, 'source': function_name}
        logger = logging.getLogger(__name__)
        logger.info(f"\n---------------------------------------------------------------\n"
                    f"{message}\n", extra=bundle)
        print(f"{message}")

    @staticmethod
    def log_warning(message: Any, module_name: str, function_name: str = inspect.currentframe().f_code.co_name):
        logging.basicConfig(filename=EventLogHelper.__get_log_file("WARNING"),
                            format=EventLogHelper.LOG_FORMAT,
                            datefmt=EventLogHelper.TIME_FORMAT,
                            level=logging.WARNING)
        bundle = {'module_name': module_name, 'source': function_name}
        logger = logging.getLogger(__name__)
        logger.warning(f"\n---------------------------------------------------------------\n"
                       f"{message}\n", extra=bundle)
        print(f"{message}")

    @staticmethod
    def log_error(message: Any, module_name: str, function_name: str = inspect.currentframe().f_code.co_name,
                  log_level=logging.ERROR, ):
        logging.basicConfig(filename=EventLogHelper.__get_log_file("ERROR"),
                            format=EventLogHelper.LOG_FORMAT,
                            datefmt=EventLogHelper.TIME_FORMAT,
                            level=log_level)
        bundle = {'module_name': module_name, 'source': function_name}
        logger = logging.getLogger(__name__)
        logger.error(f"\n---------------------------------------------------------------\n"
                     f"{message}\n", extra=bundle)
        print(f"{message}")