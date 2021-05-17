# coding: utf-8

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

from wizard.database.create_database import create_database
from wizard.database import utility as db_utils
from wizard.constants import site_const
from wizard.core import tools
from wizard.core import environment



# Python modules
import os
import time

def create_site_database(site_path):
    ''' This function init the wizard site '''
    if os.path.isdir(site_path):
        database_file = get_database_file(site_path)
        if not os.path.isfile(database_file):
            if create_database(database_file):
                create_users_table(database_file)
                create_projects_table(database_file)
        else:
            logging.warning("Database file already exists")
    else:
        logging.info("The given site path doesn't exists")

def get_database_file(site_path):
    if site_path:
        database_file = os.path.join(site_path, site_const._site_database_file_)
    else:
        database_file = None
    return database_file

def create_users_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS users (
                                        id integer PRIMARY KEY,
                                        user_name text NOT NULL,
                                        pass text NOT NULL,
                                        email text NOT NULL,
                                        administrator integer
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Users table created")

def create_projects_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS projects (
                                        id integer PRIMARY KEY,
                                        project_name text NOT NULL,
                                        project_path text NOT NULL,
                                        project_password text NOT NULL
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Projects table created")

class site:
    def __init__(self):
        self.database_file = get_database_file(environment.get_site_path())

    def create_user(self, user_name, password, email, administrator):
        exists = 0
        users_list = self.get_users_list()
        for user in users_list:
            if user_name == user[1]:
                logging.warning(f'User {user_name} already exists')
                exists = 1
        if not exists:
            sql_cmd = ''' INSERT INTO users(user_name, pass, email, administrator)
                      VALUES(?,?,?,?) '''
            if db_utils.commit_data(self.database_file, sql_cmd, (user_name, tools.encrypt_string(password), email, administrator)):
                logging.info(f"User {user_name} created")

    def get_users_list(self):
        sql_cmd = ''' SELECT * FROM users '''
        users_rows = db_utils.get_rows(self.database_file, sql_cmd)
        return users_rows

    def get_user_names_list(self):
        users_rows = self.get_users_list()
        user_names = []
        for user_row in users_rows:
            user_names.append(user_row[1])
        return user_names

    def get_user_row_by_name(self, name):
        sql_cmd = "SELECT * FROM users WHERE user_name=?"
        users_rows = db_utils.get_row_by_column_data(self.database_file, sql_cmd, name)
        return users_rows[0]
