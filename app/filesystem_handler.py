
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
    def extract_contributors_and_sources(self, data, indices, _list):
        if len(indices) == 0:
            single_contributors = set()
            sources = set()
            #TO IMPROVE REMOVING FOR LOOPS
            #contributors_list = [c.split("|") for c in contributors_list]
            #single_contributors = set(map(tuple, contributors_list))
            for l in _list:
                contributors = l[0].split("|")
                for c in contributors:
                    single_contributors.add(c)
                sources.add(l[1])
            return {'contributors': single_contributors, 'sources': sources}
            #['Selway Philip James', 'Greenwood Colin Charles', 'O Brien Edward John', 'Yorke Thomas Edward']
            #['Florence Lionel Jacques', 'Obispo Pascal Michel']
            #['Edward Sheeran', 'Edward Christopher Sheeran']
            #['Ripoll Shakira Isabel Mebarak', 'Rayo Gibo Antonio']
        else:
            idx = indices.pop()
            cur_row = data[idx]
            _list.append([cur_row[2], cur_row[3]])
            return self.extract_contributors_and_sources(data, indices, _list) 
    
    def extract_iswcs(self, _file):
        df = pd.DataFrame(_file, columns=['iswc'])
        #remove duplicates
        iswcs = list(set(df["iswc"]))
        # discard rows with null iswc
        iswcs = [elem for elem in iswcs if not(pd.isnull(elem))]# ['T0101974597', 'T9214745718', 'T0046951705', 'T9204649558']
        return iswcs

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
            data = pd.DataFrame(_file, columns=['iswc', 'title', 'contributors', 'source']).values.tolist()
            # extract all iswcs from data
            iswcs = self.extract_iswcs(_file)
            query = 'BEGIN;\n'
            for iswc in iswcs:
                # indici delle occorrenze del brano corrente in data
                indices = [i for i, x in enumerate(data) if x[0] == iswc]
                title = data[indices[0]][1]
                # sources = [s for s in data[3] for d in data if d[0] == iswc]
                # print(sources)
                # [y for y in x for x in non_flat] 
                if(pd.isnull(title)):
                    title = ''
                contributors_sources = self.extract_contributors_and_sources(data, indices, [])
                contributors = list(contributors_sources['contributors'])
                sources = list(contributors_sources['sources'])
                query = f"INSERT INTO musical_work_test (iswc, contributors, title, source) VALUES ('{iswc}', ARRAY{contributors}, '{title}', ARRAY{sources}) ON CONFLICT DO UPDATE SET contributors=ARRAY{contributors};"
                #query += ''.join(f"INSERT INTO musical_work (iswc, contributor, title) VALUES ('{iswc}', '{c}', '{title}') ON CONFLICT DO NOTHING;" for c in contributors)
            query += '\nCOMMIT;'
            print(query)
            #DB(host=self.db_config['DB_HOST'], port=self.db_config['DB_PORT'], database=self.db_config['DB_NAME'], user=self.db_config['DB_USER'], password=self.db_config['DB_PASSWORD']).executeQuery(query)
            logging.info('Finished')