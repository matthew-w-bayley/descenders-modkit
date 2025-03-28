'''
Module to test database concurrency of postgresql.
'''
import unittest
import time

class TestConcurrency(unittest.TestCase):
    
    def reset_database(self):
        drop_all = "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
        conn = self.connect()
        cur = conn.cursor()
        cur.execute(drop_all)
        with open('./src/db/schema.sql') as f:
            schema = f.read()
            cur.execute(schema)
        conn.commit()

    def connect(self):
        import psycopg2
        conn = psycopg2.connect(
            database = "postgres", 
            user = "postgres", 
            host= 'localhost',
            password = "postgres",
            port = 5432
        )
        return conn
    
    def test_concurrent_connections(self):
        self.reset_database()
        import threading
        def concurrency():
            conn = self.connect()
            cur = conn.cursor()
            cur.execute("INSERT INTO trails (world_name, trail_name) VALUES ('world', 'trail')")
            conn.commit()
            conn.close()

        # apply the same sql statement concurrently
        threads = []
        for i in range(220):
            conn = self.connect()
            t = threading.Thread(target=concurrency)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

        # check the number of records
        conn = self.connect()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM trails")
        count = cur.fetchone()[0]
        self.assertEqual(count, 220)
        conn.close()


    def test_concurrent_execution(self):
        self.reset_database()
        import threading
        conn = self.connect()
        cur = conn.cursor()
        concurrency_sql = "INSERT INTO trails (world_name, trail_name) VALUES ('world', 'trail')"
        # apply the same sql statement concurrently
        threads = []
        for i in range(200):
            t = threading.Thread(target=cur.execute, args=(concurrency_sql,))
            threads.append(t)
            t.start()
        for t in threads:
            t.join()
        conn.commit()
        # check the number of records
        cur.execute("SELECT COUNT(*) FROM trails")
        count = cur.fetchone()[0]
        self.assertEqual(count, 200)
        conn.close()
