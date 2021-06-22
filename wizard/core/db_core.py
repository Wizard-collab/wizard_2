# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import socket
import threading
import json

# PostgreSQL python modules
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Wizard modules
from wizard.core import environment
from wizard.core import socket_utils
from wizard.core import logging
logging = logging.get_logger(__name__)

class db_server(threading.Thread):
    def __init__(self, project_name=None):
        super(db_server, self).__init__()
        hostname = 'localhost'
        port = 11112
        self.server_address = socket.gethostbyname(hostname)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((hostname, port))
        self.server.listen(100) 
        self.running = True
        self.project_name = project_name
        self.site_conn = None
        self.project_conn = None

    def run(self):
        self.site_conn = create_connection('site')
        self.site_conn.autocommit = True
        if self.project_name:
            self.project_conn = create_connection(self.project_name)
            self.project_conn.autocommit = True
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn).decode('utf8')
                    if signal_as_str:
                        returned = self.execute_sql(signal_as_str)
                        conn.send(json.dumps(returned).encode('utf-8'))
                        conn.close()
            except:
                logging.error(str(traceback.format_exc()))
                continue
        if self.site_conn is not None:
            self.site_conn.close()
        if self.project_conn is not None:
            self.project_conn.close()


    def stop(self):
        self.running = False

    def execute_sql(self, signal_as_str):
        try:
            signal_dic = json.loads(signal_as_str)

            if signal_dic['level'] == 'site':
                conn = self.site_conn
            else:
                if not self.project_conn:
                    if self.project_name:
                        self.project_conn = create_connection(self.project_name)
                        self.project_conn.autocommit = True
                conn = self.project_conn
            if conn:
                rows = None
                if signal_dic['as_dict']:
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                else:
                    cursor = conn.cursor()
                if signal_dic['data']:
                    cursor.execute(signal_dic['sql'], signal_dic['data'])
                else:
                    cursor.execute(signal_dic['sql'])
                if signal_dic['fetch'] == 2:
                    rows = cursor.fetchall()
                elif signal_dic['fetch'] == 1:
                    rows = cursor.fetchone()[0]
                if not signal_dic['as_dict'] and signal_dic['fetch'] != 1:
                    if rows:
                        rows = [r[0] for r in rows]
                return rows
            else:
               logging.error("No connection")
               return None
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
            return None

def create_connection(database=None):
    try:
        conn=None
        conn = psycopg2.connect(environment.get_psql_dns(), database=database)
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None

def create_database(database):
    conn=None
    try:
        conn = create_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {database};")
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    finally:
        if conn is not None:
            conn.close()

def create_table(database, cmd):
    try:
        conn = create_connection(database)
        cursor = conn.cursor()
        cursor.execute(cmd)
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    finally:
        if conn:
            conn.close()