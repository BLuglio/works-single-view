
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileCreatedEvent
import time
from filesystem_handler import FileSystemHandler
import logging
import config
import os

class Watcher:

    def __init__(self):
        logging.basicConfig(level=logging.DEBUG)
        self.src_path = config.src_path
        self.event_observer = PollingObserver()

    def run(self):
        event_handler = FileSystemHandler()
        self.event_observer.schedule(event_handler, self.src_path)
        self.event_observer.start()
        logging.info('Initialized watcher on folder %s', self.src_path)
        # process files already in src folder
        for file in os.listdir(self.src_path):
            filename = os.path.join(self.src_path, file)
            event = FileCreatedEvent(filename)
            event_handler.on_any_event(event)
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.event_observer.stop()
        self.event_observer.join()