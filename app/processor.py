import csv
import pandas as pd
import numpy as np
from db import DB
import config
import logging

class Processor():

    # extract all iswc codes from a pandas data frame, filtering out null values and duplicates
    # @params: pandas.DataFrame object
    # @returns: list of iswc codes
    def extract_iswcs(self, df):
        df_clean = df.drop_duplicates().dropna()
        return list(df_clean["iswc"])
    
    # extract all the contributors for a given iswc, eliminating the duplicate values
    # @params: dataset, indices to consider, list of partial results
    # @returns: list of strings 
    def extract_contributors(self, data, indices, contributors_list):
        if len(indices) == 0:
            single_contributors = set()
            for c in contributors_list:
                if pd.isnull(c) or c == '':
                    single_contributors.add('')
                else:
                    _list = c.split("|")
                    for elem in _list:
                        single_contributors.add(elem)
            return list(single_contributors)
        else:
            idx = indices.pop()
            cur_row = data[idx]
            contributors_list.append(cur_row[2])
            return self.extract_contributors(data, indices, contributors_list) 

    # extracts the first non-null value found
    # @returns: string
    def extract_title(self, data, indices):
        if(len(indices) == 0):
            return ''
        else:
            idx = indices.pop()
            cur_row = data[idx]
            title = cur_row[1]
            if(pd.isnull(title)):
                return self.extract_title(data, indices)
            else: 
                return title
        
    def store(self, query) :
        DB().execute_multiple_queries(query)

    def process(self, filepath):
        logging.basicConfig(level=logging.DEBUG)
        _file = pd.read_csv(filepath)
        data = pd.DataFrame(_file, columns=['iswc', 'title', 'contributors']).values.tolist()
        df = pd.DataFrame(_file, columns=['iswc'])
        iswcs = self.extract_iswcs(df)
        queries = ""
        for iswc in iswcs:
            logging.info('Extracting metadata for ISWC: %s', iswc)
            indices = [i for i, x in enumerate(data) if x[0] == iswc]# indices of all the occurrences of current iswc in data
            title = self.extract_title(data, list(indices))
            contributors = self.extract_contributors(data, list(indices), [])
            queries += f"INSERT INTO works_single_view (iswc, contributors, title) VALUES ('{iswc}', ARRAY{contributors}::text[], '{title}') ON CONFLICT ON CONSTRAINT iswc DO UPDATE SET contributors=ARRAY{contributors}::text[], modified_at=now();\n"
        logging.info("Storing results")
        self.store(queries)