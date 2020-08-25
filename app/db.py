import psycopg2

class DB():
    def __init__(self, host, port, database, user, password):
        try:
            self.conn = psycopg2.connect(host=host, port=port, 
                dbname=database, user=user, password=password)
            self.cur = self.conn.cursor()
        except(Exception e):
            print(str(e))

    def executeQuery(self, query):
        self.cur.execute(query)
    
    def close(self):
        self.cur.close()
        self.conn.close()