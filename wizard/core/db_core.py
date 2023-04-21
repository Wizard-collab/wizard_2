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

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class db_access_singleton(metaclass=Singleton):
    def __init__(self):
        super(db_access_singleton, self).__init__()
        self.project_name = None
        self.project_conn = None
        self.repository = None
        self.repository_conn = None

    def set_repository(self, repository):
        self.repository = repository

    def set_project(self, project_name):
        self.project_name = project_name

    def execute_sql_command(self, conn,
                            sql_cmd,
                            as_dict=1,
                            data=None,
                            fetch=2):
            cursor_factory = psycopg2.extras.RealDictCursor if as_dict else None
            with conn.cursor(cursor_factory=cursor_factory) as cursor:
                if data:
                    cursor.execute(sql_cmd, data)
                else:
                    cursor.execute(sql_cmd)
                if fetch == 2:
                    rows = cursor.fetchall()
                elif fetch == 1:
                    rows = cursor.fetchone()[0] if cursor.rowcount > 0 else None
                else:
                    rows = 1
                if not as_dict and fetch != 1:
                    if rows != 1:
                        rows = [r[0] for r in rows]
            return rows

    def execute_signal(self, level, sql_cmd, as_dict=True, data=None, fetch=2):
        retries = 5
        while retries > 0:
            try:
                conn = self.get_connection(level)
                if conn:
                    rows = self.execute_sql_command(conn, sql_cmd, as_dict, data, fetch)
                    return rows
                else:
                    retries -= 1
                    if retries == 0:
                        raise
                    time.sleep(0.02)
            except:
                logger.error(f"Failed to execute SQL command: {error}")
                raise
    
    def get_connection(self, level):
        conn = None
        try:
            if level == 'repository':
                if not self.repository_conn:
                    if self.repository:
                        self.repository_conn = create_connection(self.repository)
                conn = self.repository_conn
            else:
                if not self.project_conn:
                    if self.project_name:
                        self.project_conn = create_connection(self.project_name)
                conn = self.project_conn
        except (Exception, psycopg2.DatabaseError) as error:
            logger.error(f"Failed to get a {level} database connection")
            self.repository_conn = None
            self.project_conn = None
        return conn

def create_connection(database=None):
    try:
        conn = psycopg2.connect(environment.get_psql_dns(), database=database)
        if conn and database:
            conn.autocommit=True
            logger.info(f"Wizard is connected to {database} database")
        return conn
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return

def try_connection(DNS):
    try:
        conn = psycopg2.connect(DNS)
        if conn is not None:
            conn.close()
        return 1
    except psycopg2.OperationalError as e:
        logger.error(e)
        logger.error(f"Wizard could not connect to PostgreSQL server with this DNS : {DNS}")
        return

def create_database(database):
    conn=None
    try:
        conn = create_connection()
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cur = conn.cursor()
        cur.execute(f"CREATE DATABASE {database};")
        cur.close()
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return
    finally:
        if conn is not None:
            conn.close()

def create_table(database, cmd):
    try:
        conn = create_connection(database)
        cursor = conn.cursor()
        cursor.execute(cmd)
        cursor.close()
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logger.error(error)
        return
    finally:
        if conn:
            conn.close()