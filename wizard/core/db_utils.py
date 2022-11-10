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

# The database core
# This module permits to access a given database
# and simplify the requests with python
# It permits to avoid SQL commands in the others
# wizard functions

# Python modules
import traceback
import socket
import json
import logging

# Wizard modules
from wizard.core import db_core
from wizard.core import environment
from wizard.core import socket_utils
logger = logging.getLogger(__name__)

def create_database(database):
    return db_core.create_database(database)

def create_table(database, cmd):
    return db_core.create_table(database, cmd)

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

def get_rows(level, table, column='*', order='id'):
    sql_cmd = f''' SELECT {column} FROM {table} ORDER BY {order}'''
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
        sql_cmd = f"SELECT {(', ').join(column)} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY id"
    else:
        sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY id"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, (column_tuple[1],))

def get_row_by_column_part_data(level,
                            table,
                            column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} ILIKE %s ORDER BY id"
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

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} ILIKE %s AND {second_column_tuple[0]}=%s ORDER BY id;"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, (f"%{column_tuple[1]}%",second_column_tuple[1]))
   
def get_last_row_by_column_data(level,
                            table,
                            column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY id DESC LIMIT 1;"
    if column != '*':
        as_dict=0
    else:
        as_dict=1
    return execute_sql(sql_cmd, level, as_dict, (column_tuple[1],))

def check_existence_by_multiple_data(level,
                    table,
                    columns_tuple,
                    data_tuple):

    sql_cmd = f"SELECT id FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s ORDER BY id;"
    return execute_sql(sql_cmd, level, 0, data_tuple)

def check_existence(level,
                    table,
                    column,
                    data):

    sql_cmd = f"SELECT id FROM {table} WHERE {column}=%s ORDER BY id;"
    return execute_sql(sql_cmd, level, 0, (data,))

def get_row_by_multiple_data(level,
                    table,
                    columns_tuple,
                    data_tuple,
                    column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s ORDER BY id;"
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
    
def delete_row(level, table, id, column='id'):
    sql_cmd = f'DELETE FROM {table} WHERE {column}=%s'
    return execute_sql(sql_cmd, level, 0, (id,), 0)

def delete_rows(level, table):
    sql_cmd = f'DELETE FROM {table}'
    return execute_sql(sql_cmd, level, 0, None, 0)

def check_database_existence(database):
    conn = db_core.create_connection()
    if conn is None:
        return
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute("SELECT datname FROM pg_database;")
    list_database = cur.fetchall()
    conn.close()
    if (database,) not in list_database:
        logger.debug("'{}' Database doesn't exist.".format(database))
        return
    logger.debug("'{}' Database already exist".format(database))
    return 1

def get_table_description(level, table):
    sql_cmd = f"SELECT column_name, data_type FROM information_schema.columns WHERE table_name = '{table}' order by ORDINAL_POSITION;"
    return execute_sql(sql_cmd, level, 1)

def get_tables(level):
    sql_cmd = "SELECT table_name FROM information_schema.tables WHERE (table_schema = 'public')"
    return execute_sql(sql_cmd, level, 1)

def execute_sql(sql, level, as_dict, data=None, fetch=2):
    signal_dic = dict()
    signal_dic['request'] = 'sql_cmd'
    signal_dic['sql'] = sql
    signal_dic['level'] = level
    signal_dic['as_dict'] = as_dict
    signal_dic['data'] = data
    signal_dic['fetch'] = fetch
    return socket_utils.send_signal(('localhost', environment.get_local_db_server_port()), signal_dic, timeout=10000)

def modify_db_name(level, db_name):
    signal_dic = dict()
    signal_dic['request'] = 'modify_database_name'
    signal_dic['level'] = level
    signal_dic['db_name'] = db_name
    return socket_utils.send_signal(('localhost', environment.get_local_db_server_port()), signal_dic)
