from watchdog.events import FileSystemEventHandler, LoggingEventHandler
from watchdog.observers.polling import PollingObserver
import logging
import time
import csv
import pandas as pd
from db import DB

class _CustomHandler(FileSystemEventHandler):

    def __init__(self, db_config):
        super()
        self.db_config = db_config

    def insert_data_in_DB(row):
        query = f"INSERT INTO musical_work (title, contributors, iswc, source, provider_id) VALUES '{row.title}', '{row.contributors}','{row.iswc}','{row.source}', {row.id}"
        db = DB(host=self.db_config.host, port=self.db_config.port, database=self.db_config.database, user=self.db_config.user, password=self.db_config.password)
        db.executeQuery(query)
        db.close()

    def on_created(self, event):
        if event.event_type == 'created':
            _file = pd.read_csv(event.src_path)
            for row in _file.itertuples():
                self.insert_data_in_DB(row)

class Watcher:

    def __init__(self, config):
        self.__src_path = config.src_path
        db_config = { 
            host=config.host, port=config.port, database=config.database, user=config.user, password=config.password
        }
        self.__event_observer = PollingObserver()
        self.__event_handler = _CustomHandler()

    def run(self):
        print('watcher running\n')
        self.__event_observer.schedule(self.__event_handler, self.__src_path, recursive=True)
        self.__event_observer.start()
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()

    def stop(self):
        self.__event_observer.stop()
        self.__event_observer.join()