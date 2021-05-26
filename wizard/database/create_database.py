# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sqlite3
from sqlite3 import Error

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

def create_database(db_file):
    # create a database connection to a SQLite database
    conn = None
    try:
        conn = sqlite3.connect(db_file)
        logging.info("Database file created")
    except Error as e:
        logging.error(e)
        logging.error("Can't create database file")
    finally:
        if conn:
            conn.close()
            return 1
        else:
            return None
