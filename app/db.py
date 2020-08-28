import psycopg2
import config

class DB():
    def __init__(self):
        try:
            self.conn = psycopg2.connect(host=config.DB_HOST, port=config.DB_PORT, database=config.DB_NAME, user=config.DB_USER, password=config.DB_PASSWORD)
            self.cur = self.conn.cursor()
        except Exception as e:
            print(e)

    def execute_query(self, query):
        self.cur.execute(query)
        self.close()
    
    def execute_multiple_queries(self, queries):
        self.cur.execute("BEGIN;\n" + queries + "\nCOMMIT;")
        self.close()
    
    def close(self):
        self.cur.close()
        self.conn.close()