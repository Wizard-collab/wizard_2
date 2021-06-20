# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to handle third party softwares commands
# For example if you want to save a version within a 
# Maya, the software plugin sends a socket signal
# here and waits for a return ( also socket signal )

# It roughly is a lan access to the wizard core functions

# Python modules
import socket
import sys
from threading import Thread
import time
import traceback
import json
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

class db_server(Thread):
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
                    signal_as_str = conn.recv(2048).decode('utf8')
                    if signal_as_str:
                        returned = self.execute_sql(signal_as_str)
                        conn.send(json.dumps(returned).encode('utf-8'))
            except:
                logging.error(str(traceback.format_exc()))
                continue

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
                if signal_dic['as_dict']:
                    cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
                else:
                    cursor = conn.cursor()
                if signal_dic['data']:
                    cursor.execute(signal_dic['sql'], signal_dic['data'])
                else:
                    cursor.execute(signal_dic['sql'])
                if not signal_dic['fetchone']:
                    rows = cursor.fetchall()
                else:
                    rows = cursor.fetchone()[0]
                if not signal_dic['as_dict'] and not signal_dic['fetchone']:
                    rows = [r[0] for r in rows]
                return rows
            else:
               logging.error("No connection")
               return None
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error(error)
            return None

def create_connection(database):
    try:
        conn=None
        conn = psycopg2.connect(
            host="192.168.1.21",
            database=database,
            user='pi',
            password='Tv8ams23061995')
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None