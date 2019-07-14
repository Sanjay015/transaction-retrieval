"""Module to monitor if a new file got dumped into the data directory0"""
import argparse
import logging.config
import os
import requests
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from config import DATA_LOAD_URL_PATTERN
from utils.utils import get_root
from log.logger import setup_logger

logger = logging.getLogger("watcher")


class DataWatchHandler(PatternMatchingEventHandler):
    patterns = ["*.csv"]

    def __init__(self, host="localhost", port=8000):
        super().__init__()
        self.host = host
        self.port = port
        self.url = "http://{}:{}/{}".format(self.host, self.port, DATA_LOAD_URL_PATTERN)

    def process(self, event):
        """
        Args:
            event: Event object on folder/files

        Usage:
            event.event_type
                'modified' | 'created' | 'moved' | 'deleted'
            event.is_directory
                True | False
            event.src_path
                path/to/observed/location(file|directory)
        """
        # Hit running application's URL to load data
        try:
            requests.get(self.url)
        except Exception as ex:
            logger.error("{}".format(ex))

    def on_created(self, event):
        self.process(event)


if __name__ == '__main__':
    # Logger setup
    logging.config.dictConfig(setup_logger())

    # Command Line Argument parser
    parser = argparse.ArgumentParser(description='Command Line Argument parser')
    parser.add_argument('--host', default="localhost", type=str, help='Application host')
    parser.add_argument('-p', '--port', default=8000, type=int, help='Application port')
    args = parser.parse_args()

    observer = Observer()
    # Schedule the watcher
    observer.schedule(DataWatchHandler(host=args.host, port=args.port), path=os.path.join(get_root(), "data"))

    # Starting data file watcher
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
