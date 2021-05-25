# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sqlite3
from sqlite3 import Error
import time

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

def create_connection(db_file):
    conn = None
    try:
        if db_file:
            conn = sqlite3.connect(db_file)
            logging.debug(f'*{db_file}')
        else:
            logging.error("No database file given")
    except Error as e:
        print(e)

    return conn

def create_table(db_file, cmd):
    try:
        conn = create_connection(db_file).cursor()
        conn.execute(cmd)
        return 1
    except Error as e:
        print(e)
        return 0

def create_row(db_file, table, columns, datas):

    # Construct sql command
    sql_cmd = f''' INSERT INTO {table}('''
    sql_cmd += (',').join(columns)
    sql_cmd += ') VALUES('
    data_abstract_list = []
    for item in columns:
        data_abstract_list.append('?')
    sql_cmd += (',').join(data_abstract_list)
    sql_cmd += ')'

    try:
        # Execute command
        conn = create_connection(db_file)
        cursor = conn.cursor()
        cursor.execute(sql_cmd, datas)
        conn.commit()
        logging.debug(f'*{db_file}-write')
        return cursor.lastrowid
    except Error as e:
        print(e)
        return 0

def get_rows(db_file, table, column='*'):

    sql_cmd = f''' SELECT {column} FROM {table}'''

    try:
        conn = create_connection(db_file)
        if column != '*':
            conn.row_factory = lambda cursor, row: row[0]
        else:
            conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute(sql_cmd)
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(e)
        return None

def get_row_by_column_data(db_file, table, column_tuple, column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=?"

    try:
        conn = create_connection(db_file)
        if column != '*':
            conn.row_factory = lambda cursor, row: row[0]
        else:
            conn.row_factory = dict_factory
        cursor = conn.cursor()
        cursor.execute(sql_cmd, (column_tuple[1],))
        rows = cursor.fetchall()
        return rows
    except Error as e:
        print(e)
        return None

def update_data(db_file, table, set_tuple, where_tuple):

    # Construct sql command
    sql_cmd = f''' UPDATE {table}'''
    sql_cmd += f''' SET {set_tuple[0]} = ?'''
    sql_cmd += f''' WHERE {where_tuple[0]} = ?'''

    try:
        conn = create_connection(db_file)
        cursor = conn.cursor()
        cursor.execute(sql_cmd, (set_tuple[1], where_tuple[1]))
        conn.commit()
        return 1
    except Error as e:
        print(e)
        return None

def delete_row(db_file, table, id):
    """
    Delete a task by task id
    :param conn:  Connection to the SQLite database
    :param id: id of the task
    :return:
    """
    sql = f'DELETE FROM {table} WHERE id=?'
    try:
        conn = create_connection(db_file)
        cursor = conn.cursor()
        cursor.execute(sql, (id,))
        conn.commit()
        return 1
    except Error as e:
        print(e)
        return None

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d
