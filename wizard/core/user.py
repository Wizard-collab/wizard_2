# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This wizard module is used to build the user environment
# when launching the application
# It can get the site path and some user
# preferences from $Documents/preferences.yaml

# If a site path is defined this module
# is used to get the current machine user and project
# The user logs are wrapped to the machine ip
# The machine ips are stored in the site database file

# Python modules
import yaml
import json
import os
import importlib
import sys
import shutil

# Wizard modules
from wizard.vars import user_vars
from wizard.vars import ressources
from wizard.core import image
from wizard.core import tools
from wizard.core import environment
from wizard.core import project
from wizard.core import site
from wizard.core import db_core
from wizard.core import db_utils

from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

def create_user_folders():
    # Init the user folders
    # ~/Documets/wizard/icons
    # ~/Documets/wizard/scripts
    if not os.path.isdir(user_vars._script_path_):
        os.mkdir(user_vars._script_path_)
    sys.path.append(user_vars._script_path_)
    if not os.path.isdir(user_vars._icons_path_):
        os.mkdir(user_vars._icons_path_)

def init_user_session():
    # Init the session.py file
    # This file permits to execute
    # user scripts in the
    # of the application environment
    with open(user_vars._session_file_, 'w') as f:
        f.write('')

create_user_folders()
init_user_session()

import session

class user:
    def __init__(self):
        self.get_user_prefs_dic()

    def set_psql_dns(self, host, port, user, password):
        DNS = f"host={host} port={port} user={user} password={password}"
        if db_core.try_connection(DNS):
            self.prefs_dic[user_vars._psql_dns_] = DNS
            self.write_prefs_dic()
            environment.set_psql_dns(DNS)
            return 1
        else:
            return None

    def get_psql_dns(self):
        if self.prefs_dic[user_vars._psql_dns_]:
            if db_core.try_connection(self.prefs_dic[user_vars._psql_dns_]):
                environment.set_psql_dns(self.prefs_dic[user_vars._psql_dns_])
                return 1
            else:
                self.prefs_dic[user_vars._psql_dns_] = None
                self.write_prefs_dic()
                return None
        else:
            logger.info("No postgreSQL DNS set")
            return None

    def add_context(self, context_dic):
        self.prefs_dic[user_vars._tree_context_][environment.get_project_name()] = context_dic
        self.write_prefs_dic()

    def get_context(self):
        if environment.get_project_name() in self.prefs_dic[user_vars._tree_context_].keys():
            return self.prefs_dic[user_vars._tree_context_][environment.get_project_name()]
        else:
            return None

    def get_user_prefs_dic(self):
        # Read ~/Documents/wizard/prefences.yaml
        # or init it if not found
        # return the preferences dictionnary
        self.user_prefs_file = user_vars._user_prefs_file_
        if not os.path.isdir(user_vars._user_path_):
            os.mkdir(user_vars._user_path_)
        if not os.path.isfile(self.user_prefs_file):
            self.prefs_dic = dict()
            self.prefs_dic[user_vars._psql_dns_] = None
            self.prefs_dic[user_vars._tree_context_] = dict()
            self.write_prefs_dic()
        else:
            with open(self.user_prefs_file, 'r') as f:
                self.prefs_dic = yaml.load(f, Loader=yaml.Loader)

    def write_prefs_dic(self):
        with open(self.user_prefs_file, 'w') as f:
            yaml.dump(self.prefs_dic, f)

    def execute_session(self, script):
        # Execute a custom script
        # in the application environment
        # It write the script in 
        # ~/Documents/wizard/scripts/session.py
        # and reload the "session" module
        with open(user_vars._session_file_, 'w') as f:
                f.write(script)
        try:
            importlib.reload(session)
        except:
            logger.error(sys.exc_info()[1])

    def execute_py(self, file):
        # Read a .py file and execute the data
        # with "execute_session()"
        if os.path.isfile(file):
            with open(file, 'r') as f:
                data = f.read()
            self.execute_session(data)
        else:
            logger.warning(f"{file} doesn't exists")

def log_user(user_name, password):
    if user_name in site.get_user_names_list():
        user_row = site.get_user_row_by_name(user_name)
        if tools.decrypt_string(user_row['pass'],
                                password):
            site.update_current_ip_data('user_id', user_row['id'])
            environment.build_user_env(user_name)
            logger.info(f'{user_name} signed in')
            return 1
        else:
            logger.warning(f'Wrong password for {user_name}')
            return None
    else:
        logger.error(f"{user_name} doesn't exists")
        return None

def disconnect_user():
    site.update_current_ip_data('user_id', None)
    logger.info('You are now disconnected')

def get_user():
    user_id = site.get_current_ip_data('user_id')
    if user_id:
        environment.build_user_env(user_name=site.get_user_data(user_id,
                                                                'user_name'))
        return 1
    else:
        return None

def log_project(project_name, password):
    if project_name in site.get_projects_names_list():
        project_row = site.get_project_row_by_name(project_name)
        if tools.decrypt_string(project_row['project_password'],
                                password):
            site.update_current_ip_data('project_id', project_row['id'])
            environment.build_project_env(project_name, project_row['project_path'])
            db_utils.modify_db_name('project', project_name)
            logger.info(f'Successfully signed in {project_name} project')
            project.add_user(site.get_user_row_by_name(environment.get_user(),
                                                                'id'))
            return 1
        else:
            logger.warning(f'Wrong password for {project_name}')
            return None
    else:
        logger.error(f"{project_name} doesn't exists")
        return None

def disconnect_project():
    site.update_current_ip_data('project_id', None)
    logger.info('Successfully disconnect from project')

def get_project():
    project_id = site.get_current_ip_data('project_id')
    if project_id:
        project_row = site.get_project_row(project_id) 
        environment.build_project_env(project_name=project_row['project_name'],
                                        project_path=project_row['project_path'])
        return 1
    else:
        return None