# coding: utf-8

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

from wizard.database.create_database import create_database
from wizard.database import utility as db_utils
from wizard.vars import site_vars
from wizard.core import tools
from wizard.core import environment

# Python modules
import os
import time

def init_site(site_path, admin_password, admin_email):
    database_file = create_site_database(site_path)
    if database_file:
        create_admin_user(database_file, admin_password, admin_email)

def create_site_database(site_path):
    ''' This function init the wizard site '''
    if os.path.isdir(site_path):
        database_file = get_database_file(site_path)
        if not os.path.isfile(database_file):
            if create_database(database_file):
                create_users_table(database_file)
                create_projects_table(database_file)
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

class site:
    def __init__(self):
        self.database_file = get_database_file(environment.get_site_path())

    def create_project(self, project_name, project_path, project_password, administrator_pass=''):
        if project_name not in self.get_projects_names_list():
            if project_path not in self.get_projects_paths_list():
                if tools.decrypt_string(site_vars._administrator_pass_, administrator_pass):
                    if db_utils.create_row(self.database_file,
                                    'projects', 
                                    ('project_name', 'project_path', 'project_password'), 
                                    (project_name, project_path, tools.encrypt_string(project_password))):
                        logging.info(f'Project {project_name} added to site')
                        return 1
                    else:
                        return None
                else:
                    logging.warning('Wrong administrator pass')
                    return None
            else:
                logging.warning(f'Path {project_path} already assigned to another project')
        else:
            logging.warning(f'Project {project_name} already exists')

    def get_projects_list(self):
        sql_cmd = ''' SELECT * FROM projects '''
        projects_rows = db_utils.get_rows(self.database_file, sql_cmd)
        return projects_rows

    def get_projects_names_list(self):
        projects_rows = self.get_projects_list()
        projects_names = []
        for project_row in projects_rows:
            projects_names.append(project_row[1])
        return projects_names

    def get_projects_paths_list(self):
        projects_rows = self.get_projects_list()
        projects_paths = []
        for project_row in projects_rows:
            projects_paths.append(project_row[2])
        return projects_paths

    def get_project_row_by_name(self, name):
        projects_rows = db_utils.get_row_by_column_data(self.database_file,
                                                        'projects',
                                                        ('project_name', name))
        return projects_rows[0]

    def get_project_path_by_name(self, name):
        return self.get_project_row_by_name(name)[2]

    def modify_project_password(self, project_name, project_password, new_password, administrator_pass=''):
        if tools.decrypt_string(site_vars._administrator_pass_, administrator_pass):
            if project_name in self.get_projects_names_list():
                if tools.decrypt_string(self.get_project_row_by_name(project_name)[3], project_password):
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
            if tools.decrypt_string(site_vars._administrator_pass_, administrator_pass):
                administrator = 1
            if db_utils.create_row(self.database_file,
                            'users', 
                            ('user_name', 'pass', 'email', 'administrator'), 
                            (user_name, tools.encrypt_string(password), email, administrator)):

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
            logging.warning('User {user_name} already exists')
            return None

    def upgrade_user_privilege(self, user_name, administrator_pass):
        if user_name in self.get_user_names_list():
            user_row = self.get_user_row_by_name(user_name)
            if not user_row[4]:
                if tools.decrypt_string(site_vars._administrator_pass_, administrator_pass):
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
            if user_row[4]:
                if tools.decrypt_string(site_vars._administrator_pass_, administrator_pass):
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
            if tools.decrypt_string(user_row[2], password):
                if db_utils.update_data(self.database_file,
                                        'users',
                                        ('pass', tools.encrypt_string(new_password)),
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
        users_rows = db_utils.get_row_by_column_data(self.database_file, 'users', ('user_name', name))
        return users_rows[0]
