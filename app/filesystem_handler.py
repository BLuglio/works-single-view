
from watchdog.events import FileSystemEventHandler
from processor import Processor
import logging

class FileSystemHandler(FileSystemEventHandler):

    def __init__(self):
        super()
        logging.basicConfig(level=logging.DEBUG)
        self.processor = Processor()
    
    def is_allowed_file(self, _file):
        if not '.csv' in str(_file):
            return False
        return True

    def on_any_event(self, event):
        if event.event_type == 'created':
            _file = event.src_path
            if self.is_allowed_file(_file):
                logging.info('Processing file: %s', event.src_path.split("/")[len(event.src_path.split("/"))-1])
                self.processor.process(_file)
                logging.info('Finished')