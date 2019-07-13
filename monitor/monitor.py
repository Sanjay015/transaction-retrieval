"""Module to monitor if a new file got dumped into the data directory0"""
import logging
import logging.config
import os
import time
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

from utils.utils import get_root
from log.logger import setup_logger

logger = logging.getLogger("watcher")


class DataWatcherHandler(PatternMatchingEventHandler):
    patterns = ["*.csv"]

    @staticmethod
    def process(event):
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
        # TODO: Call data update API
        logger.debug("{} : {}".format(event.src_path, event.event_type))

    def on_created(self, event):
        self.process(event)


if __name__ == '__main__':
    # Logger setup
    logging.config.dictConfig(setup_logger())

    args = [os.path.join(get_root(), "data")]
    observer = Observer()
    observer.schedule(DataWatcherHandler(), path=args[0] if args else '.')
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()

    observer.join()
