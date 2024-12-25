import sqlite3
import os

class StoreInteractions:

    conn = None
    cursor = None
    count = 0

    def __init__(self):
        self.conn = self.open_sqlite()
        self.cursor = self.conn.cursor()
        self.init_sqlite()

    def open_sqlite(self):
        return sqlite3.connect(f"./results/{os.environ['API']}/{os.environ['TOOL']}/{os.environ['RUN']}/results.db")
    
    def init_sqlite(self):
        self.cursor.execute('CREATE TABLE interactions (id integer PRIMARY KEY, request_method text, request_path text, request_headers text, request_content text, request_timestamp real, response_status_code integer, response_headers text, response_content text, response_timestamp real)')
        self.conn.commit()
    
    def response(self, flow):
        self.cursor.execute('INSERT INTO interactions (request_method, request_path, request_headers, request_content, request_timestamp, response_status_code, response_headers, response_content, response_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)', (flow.request.method, flow.request.path, bytes(flow.request.headers).decode('utf-8'), flow.request.content.decode('utf-8'), flow.request.timestamp_start, flow.response.status_code, bytes(flow.response.headers).decode('utf-8'), flow.response.content.decode('utf-8'), flow.response.timestamp_start))
        self.count += 1
        if self.count % 100 == 0:
            self.conn.commit()

addons = [StoreInteractions()]





