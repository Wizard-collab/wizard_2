# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to manage and access 
# the site database

# The site database stores the following informations:
#       - The users list ( name, hashed password, email )
#       - The projects list ( name, path, hashed password )
#       - The ip wraps ( roughly looks like cookies in web )

# Python modules
import os
import time
import socket

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

from wizard.database.create_database import create_database
from wizard.database import utility as db_utils
from wizard.vars import site_vars
from wizard.core import tools
from wizard.core import environment

class site:
    def __init__(self):
        self.database_file = get_database_file(environment.get_site_path())

    def create_project(self, project_name, project_path, project_password):
        if project_name not in self.get_projects_names_list():
            if project_path not in self.get_projects_paths_list():
                if self.get_user_row_by_name(environment.get_user())['pass']:
                    if db_utils.create_row(self.database_file,
                                    'projects', 
                                    ('project_name', 'project_path', 'project_password'), 
                                    (project_name,
                                    project_path,
                                    tools.encrypt_string(project_password))):
                        logging.info(f'Project {project_name} added to site')
                        return 1
                    else:
                        return None
                else:
                    logging.warning("You need to be administrator to create a project")
                    return None
            else:
                logging.warning(f'Path {project_path} already assigned to another project')
        else:
            logging.warning(f'Project {project_name} already exists')

    def get_administrator_pass(self):
        return self.get_user_row_by_name('admin')['pass']

    def get_projects_list(self):
        projects_rows = db_utils.get_rows(self.database_file, 'projects')
        return projects_rows

    def get_projects_names_list(self):
        projects_rows = db_utils.get_rows(self.database_file, 'projects', 'project_name')
        return projects_rows

    def get_projects_paths_list(self):
        projects_rows = db_utils.get_rows(self.database_file, 'projects', 'project_path')
        return projects_rows

    def get_project_row_by_name(self, name):
        projects_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'projects',
                                                        ('project_name', name))
        return projects_rows[0]

    def get_project_row(self, project_id, column='*'):
        projects_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'projects',
                                                        ('id', project_id),
                                                        column)
        return projects_rows[0]

    def get_project_path_by_name(self, name):
        return self.get_project_row_by_name(name)['project_path']

    def modify_project_password(self,
                                project_name,
                                project_password,
                                new_password,
                                administrator_pass=''):
        if tools.decrypt_string(self.get_administrator_pass(),
                                administrator_pass):
            if project_name in self.get_projects_names_list():
                if tools.decrypt_string(
                        self.get_project_row_by_name(project_name)['project_password'],
                        project_password):
                    if db_utils.update_data(self.database_file,
                                'projects',
                                ('project_password', tools.encrypt_string(new_password)),
                                ('project_name', project_name)):
                            logging.info(f'{project_name} password modified')
                            return 1
                    else:
                        return None
                else:
                    logging.warning(f'Wrong password for {project_name}')
            else:
                logging.warning(f'{project_name} not found')
        else:
            logging.warning('Wrong administrator pass')

    def create_user(self, user_name, password, email, administrator_pass=''):
        if user_name not in self.get_user_names_list():
            administrator = 0
            if tools.decrypt_string(self.get_administrator_pass(),
                                    administrator_pass):
                administrator = 1
            if db_utils.create_row(self.database_file,
                        'users', 
                        ('user_name', 'pass', 'email', 'administrator'), 
                        (user_name, tools.encrypt_string(password),
                            email, administrator)):

                info = f"User {user_name} created"
                if administrator:
                    info += ' ( privilege : administrator )'
                else:
                    info += ' ( privilege : user )'
                logging.info(info)
                return 1
            else:
                return None
        else:
            logging.warning(f'User {user_name} already exists')
            return None

    def upgrade_user_privilege(self, user_name, administrator_pass):
        if user_name in self.get_user_names_list():
            user_row = self.get_user_row_by_name(user_name)
            if not user_row[4]:
                if tools.decrypt_string(self.get_administrator_pass(),
                                            administrator_pass):
                    if db_utils.update_data(self.database_file,
                                            'users',
                                            ('administrator',1),
                                            ('user_name', user_name)):
                        logging.info(f'Administrator privilege set for {user_name}')
                else:
                    logging.warning('Wrong administrator pass')
            else:
                logging.info(f'User {user_name} is already administrator')
        else:
            logging.error(f'{user_name} not found')

    def downgrade_user_privilege(self, user_name, administrator_pass):
        if user_name in self.get_user_names_list():
            user_row = self.get_user_row_by_name(user_name)
            if user_row['administrator']:
                if tools.decrypt_string(self.get_administrator_pass(),
                                            administrator_pass):
                    if db_utils.update_data(self.database_file,
                                            'users',
                                            ('administrator',0),
                                            ('user_name', user_name)):
                        logging.info(f'Privilege downgraded to user for {user_name}')
                        return 1
                else:
                    logging.warning('Wrong administrator pass')
                    return None
            else:
                logging.info(f'User {user_name} is not administrator')
                return None
        else:
            logging.error(f'{user_name} not found')
            return None

    def modify_user_password(self, user_name, password, new_password):
        if user_name in self.get_user_names_list():
            user_row = self.get_user_row_by_name(user_name)
            if tools.decrypt_string(user_row['pass'], password):
                if db_utils.update_data(self.database_file,
                                        'users',
                                        ('pass',
                                            tools.encrypt_string(new_password)),
                                        ('user_name', user_name)):
                        logging.info(f'{user_name} password modified')
                        return 1
                else:
                    return None
            else:
                logging.warning(f'Wrong password for {user_name}')
                return None
        else:
            logging.error(f'{user_name} not found')
            return None

    def get_users_list(self):
        users_rows = db_utils.get_rows(self.database_file, 'users')
        return users_rows

    def get_user_names_list(self):
        users_rows = db_utils.get_rows(self.database_file, 'users', 'user_name')
        return users_rows

    def get_user_row_by_name(self, name, column='*'):
        users_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'users',
                                                        ('user_name', name),
                                                        column)
        return users_rows[0]

    def get_user_row(self, user_id, column='*'):
        users_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'users',
                                                        ('id', user_id),
                                                        column)
        return users_rows[0]

    def is_admin(self):
        is_admin = self.get_user_row_by_name(environment.get_user(), 'administrator')
        if not is_admin:
            logging.info("You are not administrator")
        return is_admin

    def get_ips(self, column='*'):
        ip_rows = db_utils.get_rows(self.database_file, 'ips_wrap', column)
        return ip_rows

    def add_ip_user(self):
        ip = socket.gethostbyname(socket.gethostname())
        ip_rows = self.get_ips('ip')
        if not ip_rows:
            ip_rows=[]
        if ip not in ip_rows:
            if db_utils.create_row(self.database_file,
                                'ips_wrap', 
                                ('ip', 'user_id', 'project_id'), 
                                (ip, None, None)):
                logging.debug("Machine ip added to ips wrap table")

    def update_current_ip_data(self, column, data):
        ip = socket.gethostbyname(socket.gethostname())
        if db_utils.update_data(self.database_file,
                                        'ips_wrap',
                                        (column, data),
                                        ('ip', ip)):
            logging.debug("Ip wrap data updated")

    def get_current_ip_data(self, column='*'):
        ip = socket.gethostbyname(socket.gethostname())
        ip_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'ips_wrap',
                                                        ('ip', ip),
                                                        column)
        return ip_rows[0]

def init_site(site_path, admin_password, admin_email):
    database_file = create_site_database(site_path)
    if database_file:
        create_admin_user(database_file, admin_password, admin_email)

def create_site_database(site_path):
    if os.path.isdir(site_path):
        database_file = get_database_file(site_path)
        if not os.path.isfile(database_file):
            if create_database(database_file):
                create_users_table(database_file)
                create_projects_table(database_file)
                create_ip_wrap_table(database_file)
                return database_file
        else:
            logging.warning("Database file already exists")
            return None
    else:
        logging.info("The given site path doesn't exists")
        return None

def create_admin_user(database_file, admin_password, admin_email):
    if db_utils.create_row(database_file,
                            'users', 
                            ('user_name', 'pass', 'email', 'administrator'), 
                            ('admin', tools.encrypt_string(admin_password), admin_email, 1)):
        logging.info('Admin user created')

def get_database_file(site_path):
    if site_path:
        database_file = os.path.join(site_path, site_vars._site_database_file_)
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

def create_ip_wrap_table(database_file):
    sql_cmd = """ CREATE TABLE IF NOT EXISTS ips_wrap (
                                        id integer PRIMARY KEY,
                                        ip text NOT NULL UNIQUE,
                                        user_id text,
                                        project_id,
                                        FOREIGN KEY (user_id) REFERENCES users (id)
                                        FOREIGN KEY (project_id) REFERENCES projects (id)
                                    );"""
    if db_utils.create_table(database_file, sql_cmd):
        logging.info("Ips wrap table created")
