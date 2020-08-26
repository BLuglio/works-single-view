
from watchdog.observers.polling import PollingObserver
import time
from filesystem_handler import FileSystemHandler
import logging

class Watcher:

    def __init__(self, config):
        logging.basicConfig(level=logging.DEBUG)
        self.__src_path = config['src_path']
        self.__event_observer = PollingObserver()
        self.__event_handler = FileSystemHandler(config['db_config'])

    def run(self):
        self.__event_observer.schedule(self.__event_handler, self.__src_path, recursive=True)
        self.__event_observer.start()
        logging.info('Initialized watcher on folder %s', self.__src_path)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()