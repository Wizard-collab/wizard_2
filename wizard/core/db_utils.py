# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# The database core
# This module permits to access a given database
# and simplify the requests with python
# It permits to avoid SQL commands in the others
# wizard functions

# Python modules
import traceback
import socket
import json

# Wizard modules
from wizard.core import db_core
from wizard.core import socket_utils
from wizard.vars import db_vars
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

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
    
def delete_row(level, table, id):
    sql_cmd = f'DELETE FROM {table} WHERE id=%s'
    return execute_sql(sql_cmd, level, 0, (id,), 0)

def check_database_existence(database):
    conn = db_core.create_connection()
    if conn is not None:
        conn.autocommit = True
        cur = conn.cursor()
        cur.execute("SELECT datname FROM pg_database;")
        list_database = cur.fetchall()
        conn.close()
        if (database,) in list_database:
            logger.debug("'{}' Database already exist".format(database))
            return 1
        else:
            logger.debug("'{}' Database doesn't exist.".format(database))
            return None

def execute_sql(sql, level, as_dict, data=None, fetch=2):
    signal_dic = dict()
    signal_dic['request'] = 'sql_cmd'
    signal_dic['sql'] = sql
    signal_dic['level'] = level
    signal_dic['as_dict'] = as_dict
    signal_dic['data'] = data
    signal_dic['fetch'] = fetch
    return socket_utils.send_signal(db_vars._LOCAL_DNS_, signal_dic)

def modify_db_name(level, db_name):
    signal_dic = dict()
    signal_dic['request'] = 'modify_database_name'
    signal_dic['level'] = level
    signal_dic['db_name'] = db_name
    return socket_utils.send_signal(db_vars._LOCAL_DNS_, signal_dic)
