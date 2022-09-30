# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Python modules
import threading
import traceback
import json
import time
import logging

# PostgreSQL python modules
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT

# Wizard modules
from wizard.core import environment
from wizard.core import socket_utils
logger = logging.getLogger(__name__)

class db_server(threading.Thread):
    def __init__(self, project_name=None):
        super(db_server, self).__init__()

        self.port = socket_utils.get_port('localhost')
        environment.set_local_db_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(('localhost', self.port))
        self.running = True
        self.project_name = None
        self.repository = None
        self.repository_conn = None
        self.project_conn = None

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn)
                    if signal_as_str:
                        returned = self.execute_signal(signal_as_str.decode('utf8'))
                        socket_utils.send_signal_with_conn(conn, returned)
                        conn.close()
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))
                continue
                
        if self.repository_conn is not None:
            self.repository_conn.close()
        if self.project_conn is not None:
            self.project_conn.close()

    def stop(self):
        self.server.close()
        self.running = False

    def execute_signal(self, signal_as_str):
        signal_dic = json.loads(signal_as_str)
        rows = None
        retry_count = 0
        if signal_dic['request'] == 'sql_cmd':
            while rows is None:
                try:
                    if signal_dic['level'] == 'repository':
                        if not self.repository_conn:
                            if self.repository:
                                self.repository_conn = create_connection(self.repository)
                        conn = self.repository_conn
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
                        self.repository_conn = None
                        self.project_conn = None
                except (Exception, psycopg2.DatabaseError) as error:
                    logger.error(error)
                    self.repository_conn = None
                    self.project_conn = None
                if retry_count == 5:
                    logger.error("Database max retry reached ( 5 ). Can't access database")
                    time.sleep(0.02)
                    return None
                retry_count += 1
                logger.error(f"Can't reach database, retrying ( {retry_count} )")

        elif signal_dic['request'] == 'modify_database_name':
            if signal_dic['level'] == 'repository':
                self.repository = signal_dic['db_name']
                if self.repository_conn:
                    self.repository_conn.close()
                self.repository_conn = create_connection(self.repository)
            else:
                self.project_name = signal_dic['db_name']
                if self.project_conn:
                    self.project_conn.close()
                self.project_conn = create_connection(self.project_name)
            return 1
        elif signal_dic['request'] == 'port':
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