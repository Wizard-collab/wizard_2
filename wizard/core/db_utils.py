# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# The database core
# This module permits to access a given database
# and simplify the requests with python
# It permits to avoid SQL commands in the others
# wizard functions

# Python modules
import psycopg2
import psycopg2.extras
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import time
import traceback
import os
import socket
import json
from wizard.core import socket_utils

# Wizard modules
from wizard.core import environment
from wizard.core import db_core

from wizard.core import logging
logging = logging.get_logger(__name__)

def create_database(database):
    conn=None
    try:
        conn = psycopg2.connect(environment.get_psql_dns())
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
        conn = db_core.create_connection(database)
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

def create_row(level, table, columns, datas):
    sql_cmd = f''' INSERT INTO {table}('''
    sql_cmd += (',').join(columns)
    sql_cmd += ') VALUES('
    data_abstract_list = []
    for item in columns:
        data_abstract_list.append('%s')
    sql_cmd += (',').join(data_abstract_list)
    sql_cmd += ') RETURNING id;'
    return execute_sql(sql_cmd, level, 0, datas, 1)

def get_rows(level, table, column='*'):
    sql_cmd = f''' SELECT {column} FROM {table}'''
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict)

def get_row_by_column_data(level,
                            table,
                            column_tuple,
                            column='*'):
    if type(column)==list:
        sql_cmd = f"SELECT {(', ').join(column)} FROM {table} WHERE {column_tuple[0]}=%s"
    else:
        sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, (column_tuple[1],))

def get_row_by_column_part_data(level,
                            table,
                            column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} LIKE %s"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, (f"%{column_tuple[1]}%",))

def get_row_by_column_part_data_and_data(level,
                            table,
                            column_tuple,
                            second_column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} LIKE %s AND {second_column_tuple[0]}=%s;"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, (f"%{column_tuple[1]}%",second_column_tuple[1]))
   
def get_last_row_by_column_data(level,
                            table,
                            column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY rowid DESC LIMIT 1;"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, (column_tuple[1],))

def check_existence_by_multiple_data(level,
                    table,
                    columns_tuple,
                    data_tuple):

    sql_cmd = f"SELECT id FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s;"
    return execute_sql(sql_cmd, level, 0, data_tuple)

def check_existence(level,
                    table,
                    column,
                    data):

    sql_cmd = f"SELECT id FROM {table} WHERE {column}=%s;"
    return execute_sql(sql_cmd, level, 0, (data,))

def get_row_by_multiple_data(level,
                    table,
                    columns_tuple,
                    data_tuple,
                    column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s;"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, data_tuple)

def update_data(level,
                    table,
                    set_tuple,
                    where_tuple):

    sql_cmd = f''' UPDATE {table}'''
    sql_cmd += f''' SET {set_tuple[0]} = %s'''
    sql_cmd += f''' WHERE {where_tuple[0]} = %s'''
    return execute_sql(sql_cmd, level, 0, (set_tuple[1], where_tuple[1]), 0)
    
def delete_row(level, table, id):
    sql_cmd = f'DELETE FROM {table} WHERE id=%s'
    return execute_sql(sql_cmd, level, 0, (id,), 0)

def check_database_existence(database):
    conn = None
    try:
        conn = psycopg2.connect(environment.get_psql_dns())
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None

    if conn is not None:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        list_database = cur.fetchall()
        conn.close()
        if (database,) in list_database:
            logging.debug("'{}' Database already exist".format(database))
            return 1
        else:
            logging.debug("'{}' Database doesn't exist.".format(database))
            return None

def execute_sql(sql, level, as_dict, data=None, fetch=2):
    signal_dic = dict()
    signal_dic['sql'] = sql
    signal_dic['level'] = level
    signal_dic['as_dict'] = as_dict
    signal_dic['data'] = data
    signal_dic['fetch'] = fetch
    signal_as_str = json.dumps(signal_dic)
    return send_signal(signal_as_str)

def send_signal(signal_as_str):
    try:
        host_name = 'localhost'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host_name, 11112))
        server.settimeout(5.0)
        server.send(signal_as_str.encode('utf8'))
        returned = socket_utils.recvall(server).decode('utf8')
        server.close()
        return json.loads(returned)
    except ConnectionRefusedError:
        logging.error("No wizard local server found. Please verify if Wizard is openned")
        return None
    except socket.timeout:
        logging.error("Wizard has been too long to give a response, please retry.")
        return None
