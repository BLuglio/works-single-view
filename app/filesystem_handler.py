
from watchdog.events import FileSystemEventHandler
import csv
import pandas as pd
import numpy as np
from db import DB
import logging

class FileSystemHandler(FileSystemEventHandler):

    def __init__(self, db_config):
        super()
        self.db_config = db_config

    # extract all the contributors for a given iswc, eliminating the duplicate values
    # @params: dataset, indices to consider, list of partial results
    # @returns: list of strings 
    def extract_contributors(self, data, indices, contributors_list):
        if len(indices) == 0:
            single_contributors = set()
            #TO IMPROVE
            #contributors_list = [c.split("|") for c in contributors_list]
            #single_contributors = set(map(tuple, contributors_list))
           
            for c in contributors_list:
                _list = c.split("|")
                for elem in _list:
                    single_contributors.add(elem)
            return list(single_contributors)
            #['Selway Philip James', 'Greenwood Colin Charles', 'O Brien Edward John', 'Yorke Thomas Edward']
            #['Florence Lionel Jacques', 'Obispo Pascal Michel']
            #['Edward Sheeran', 'Edward Christopher Sheeran']
            #['Ripoll Shakira Isabel Mebarak', 'Rayo Gibo Antonio']

        else:
            idx = indices.pop()
            cur_row = data[idx]
            contributors_list.append(cur_row[2])
            return self.extract_contributors(data, indices, contributors_list) 

    def on_any_event(self, event):
        if event.event_type == 'created':
            logging.basicConfig(level=logging.DEBUG)
            logging.info('Found new file: %s', event.src_path.split("/")[len(event.src_path.split("/"))-1])
            _file = pd.read_csv(event.src_path)
            ### data pre processing: ###
            #   1) filter columns
            #   2) take all iswcs without duplicates and discard the rows with a null iswc
            #   3) for each iswc extract the contributors
            logging.info('Beginning csv processing')
            data = pd.DataFrame(_file, columns=['iswc', 'title', 'contributors']).values.tolist()
            # extract all iswcs
            df = pd.DataFrame(_file, columns=['iswc'])
            #no duplicates
            iswcs = list(set(df["iswc"]))
            # discard rows with no iswc
            iswcs = [elem for elem in iswcs if not(pd.isnull(elem))]# ['T0101974597', 'T9214745718', 'T0046951705', 'T9204649558']
            query = 'BEGIN;\n'
            for iswc in iswcs:
                # indici delle occorrenze del brano corrente in data
                indices = [i for i, x in enumerate(data) if x[0] == iswc]
                title = data[indices[0]][1]
                if(pd.isnull(title)):
                    title = ''
                contributors = self.extract_contributors(data, indices, [])
                query += ''.join(f"INSERT INTO musical_work (iswc, contributor, title) VALUES ('{iswc}', '{c}', '{title}') ON CONFLICT DO NOTHING;" for c in contributors)
            query += '\nCOMMIT;'
            DB(host=self.db_config['DB_HOST'], port=self.db_config['DB_PORT'], database=self.db_config['DB_NAME'], user=self.db_config['DB_USER'], password=self.db_config['DB_PASSWORD']).executeQuery(query)
            logging.info('Finished')