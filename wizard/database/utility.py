# conding: utf-8

import sqlite3
from sqlite3 import Error

from wizard.core import logging
logging = logging.get_logger(__name__)

def create_connection(db_file):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        if db_file:
            conn = sqlite3.connect(db_file)
        else:
            logging.error("No database file given")
    except Error as e:
        print(e)

    return conn

def create_table(db_file, cmd):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = create_connection(db_file).cursor()
        c.execute(cmd)
        return 1
    except Error as e:
        print(e)
        return 0

def commit_data(db_file, cmd, data_tuple):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        conn = create_connection(db_file)
        c = conn.cursor()
        c.execute(cmd, data_tuple)
        conn.commit()
        return 1
    except Error as e:
        print(e)
        return 0

def get_rows(db_file, cmd):
    try:
        conn = create_connection(db_file)
        cur = conn.cursor()
        cur.execute(cmd)
        rows = cur.fetchall()
        return rows
    except Error as e:
        print(e)
        return None

def get_row_by_column_data(db_file, cmd, data):
    """
    Query tasks by priority
    :param conn: the Connection object
    :param priority:
    :return:
    """
    try:
        conn = create_connection(db_file)
        cur = conn.cursor()
        cur.execute(cmd, (data,))
        rows = cur.fetchall()
        return rows
    except Error as e:
        print(e)
        return None