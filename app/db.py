import psycopg2

class DB():
    def __init__(self, host, port, database, user, password):
        try:
            self.conn = psycopg2.connect(host=host, port=port, 
                dbname=database, user=user, password=password)
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