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

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

def create_database(database):
    conn=None
    try:
        conn = psycopg2.connect(
            host="192.168.1.21",
            port='5432',
            user='pi',
            password='Tv8ams23061995')
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

def create_row(conn, table, columns, datas):
    sql_cmd = f''' INSERT INTO {table}('''
    sql_cmd += (',').join(columns)
    sql_cmd += ') VALUES('
    data_abstract_list = []
    for item in columns:
        data_abstract_list.append('%s')
    sql_cmd += (',').join(data_abstract_list)
    sql_cmd += ') RETURNING id;'
    try:
        cursor = conn.cursor()
        cursor.execute(sql_cmd, datas)
        conn.commit()
        return cursor.fetchone()[0]
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None

def get_rows(conn, table, column='*'):
    sql_cmd = f''' SELECT {column} FROM {table}'''
    try:
        #conn = create_connection(conn)
        if column != '*':
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql_cmd)
        rows = cursor.fetchall()
        if column != '*':
            rows = [r[0] for r in rows]
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def get_row_by_column_data(conn,
                            table,
                            column_tuple,
                            column='*'):
    if type(column)==list:
        sql_cmd = f"SELECT {(', ').join(column)} FROM {table} WHERE {column_tuple[0]}=%s"
    else:
        sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s"
    try:
        if column != '*' and type(column)!=list:
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        #cursor = conn.cursor()
        cursor.execute(sql_cmd, (column_tuple[1],))
        rows = cursor.fetchall()
        if column != '*':
            rows = [r[0] for r in rows]
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def get_row_by_column_part_data(conn,
                            table,
                            column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} LIKE %s"
    try:
        #conn = create_connection(conn)
        if column != '*':
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql_cmd, (f"%{column_tuple[1]}%",))
        rows = cursor.fetchall()
        if column != '*':
            rows = [r[0] for r in rows]
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def get_row_by_column_part_data_and_data(conn,
                            table,
                            column_tuple,
                            second_column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]} LIKE %s AND {second_column_tuple[0]}=%s;"
    try:
        #conn = create_connection(conn)
        if column != '*':
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql_cmd, (f"%{column_tuple[1]}%",second_column_tuple[1]))
        rows = cursor.fetchall()
        if column != '*':
            rows = [r[0] for r in rows]
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def get_last_row_by_column_data(conn,
                            table,
                            column_tuple,
                            column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {column_tuple[0]}=%s ORDER BY rowid DESC LIMIT 1;"
    try:
        #conn = create_connection(conn)
        if column != '*':
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql_cmd, (column_tuple[1],))
        rows = cursor.fetchall()
        if column != '*':
            rows = [r[0] for r in rows]
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def check_existence_by_multiple_data(conn,
                    table,
                    columns_tuple,
                    data_tuple):

    sql_cmd = f"SELECT id FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s;"
    try:
        #conn = create_connection(conn)
        cursor = conn.cursor()
        cursor.execute(sql_cmd, data_tuple)
        rows = cursor.fetchall()

        return len(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def check_existence(conn,
                    table,
                    column,
                    data):

    sql_cmd = f"SELECT id FROM {table} WHERE {column}=%s;"
    try:
        #conn = create_connection(conn)
        cursor = conn.cursor()
        cursor.execute(sql_cmd, (data, ))
        rows = cursor.fetchall()
        return len(rows)
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def get_row_by_multiple_data(conn,
                    table,
                    columns_tuple,
                    data_tuple,
                    column='*'):

    sql_cmd = f"SELECT {column} FROM {table} WHERE {columns_tuple[0]}=%s AND {columns_tuple[1]}=%s;"
    try:
        #conn = create_connection(conn)
        if column != '*':
            cursor = conn.cursor()
        else:
            cursor = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(sql_cmd, (data_tuple[0], data_tuple[1]))
        rows = cursor.fetchall()
        if column != '*':
            rows = [r[0] for r in rows]
        return rows
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def update_data(conn,
                    table,
                    set_tuple,
                    where_tuple):

    sql_cmd = f''' UPDATE {table}'''
    sql_cmd += f''' SET {set_tuple[0]} = %s'''
    sql_cmd += f''' WHERE {where_tuple[0]} = %s'''
    try:
        #conn = create_connection(conn)
        cursor = conn.cursor()
        cursor.execute(sql_cmd, (set_tuple[1], where_tuple[1]))
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''
def delete_row(conn, table, id):
    sql = f'DELETE FROM {table} WHERE id=%s'
    try:
        #conn = create_connection(conn)
        cursor = conn.cursor()
        cursor.execute(sql, (id,))
        conn.commit()
        return 1
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
        return None
    '''
    finally:
        if conn:
            conn.close()
    '''

def check_database_existence(database):
    conn = None
    try:
        conn = psycopg2.connect(
                                host='192.168.1.21',
                                port='5432',
                                user='pi',
                                password='Tv8ams23061995')
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
