# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import threading
import traceback
import json
import time

# PostgreSQL python modules
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Wizard modules
from wizard.core import environment
from wizard.core import socket_utils
from wizard.vars import db_vars
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class db_server(threading.Thread):
    def __init__(self, project_name=None):
        super(db_server, self).__init__()
        self.server, self.server_address = socket_utils.get_server(db_vars._LOCAL_DNS_)
        self.running = True
        self.project_name = None
        self.site = None
        self.site_conn = None
        self.project_conn = None

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn).decode('utf8')
                    if signal_as_str:
                        returned = self.execute_signal(signal_as_str)
                        socket_utils.send_signal_with_conn(conn, returned)
                        #conn.send(json.dumps(returned).encode('utf-8'))
                        conn.close()
            except:
                logger.error(str(traceback.format_exc()))
                continue
        if self.site_conn is not None:
            self.site_conn.close()
        if self.project_conn is not None:
            self.project_conn.close()

    def stop(self):
        self.running = False

    def execute_signal(self, signal_as_str):
            signal_dic = json.loads(signal_as_str)
            if signal_dic['request'] == 'sql_cmd':
                try:
                    if signal_dic['level'] == 'site':
                        if not self.site_conn:
                            if self.site:
                                self.site_conn = create_connection(self.site)
                        conn = self.site_conn
                    else:
                        if not self.project_conn:
                            if self.project_name:
                                self.project_conn = create_connection(self.project_name)
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
                        else:
                            rows = 1
                        if not signal_dic['as_dict'] and signal_dic['fetch'] != 1:
                            if rows != 1:
                                rows = [r[0] for r in rows]
                        return rows
                    else:
                       logger.error("No connection")
                       return None
                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(error)
                    return None
            elif signal_dic['request'] == 'modify_database_name':
                if signal_dic['level'] == 'site':
                    self.site = signal_dic['db_name']
                    if self.site_conn:
                        self.site_conn.close()
                    self.site_conn = create_connection(self.site)
                else:
                    self.project_name = signal_dic['db_name']
                    if self.project_conn:
                        self.project_conn.close()
                    self.project_conn = create_connection(self.project_name)
                return 1


def create_connection(database=None):
    try:
        conn=None
        conn = psycopg2.connect(environment.get_psql_dns(), database=database)
        if conn and database:
            conn.autocommit=True
            logger.info(f"Wizard is connected to {database} database")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return None

def try_connection(DNS):
    try:
        conn=None
        conn = psycopg2.connect(DNS)
        if conn is not None:
            conn.close()
        return 1
    except psycopg2.OperationalError as e:
        logger.error(e)
        logger.error(f"Wizard could not connect to PostgreSQL server with this DNS : {DNS}")
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
        logger.error(error)
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
        logger.error(error)
        return None
    finally:
        if conn:
            conn.close()