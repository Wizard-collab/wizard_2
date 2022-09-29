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

# This wizard module is used to build the user environment
# when launching the application
# It can get the repository path and some user
# preferences from $Documents/preferences.yaml

# If a repository path is defined this module
# is used to get the current machine user and project
# The user logs are wrapped to the machine ip
# The machine ips are stored in the repository database file

# Python modules
import yaml
import json
import os
import importlib
import sys
import shutil
import logging

# Wizard modules
from wizard.vars import user_vars
from wizard.vars import ressources
from wizard.core import image
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import environment
from wizard.core import project
from wizard.core import repository
from wizard.core import db_core
from wizard.core import db_utils
from wizard.core import team_client

logger = logging.getLogger(__name__)

def create_user_folders():
    # Init the user folders
    # ~/Documets/wizard/icons
    # ~/Documets/wizard/scripts
    if not path_utils.isdir(user_vars._script_path_):
        path_utils.makedirs(user_vars._script_path_)
    sys.path.append(user_vars._script_path_)
    if not path_utils.isdir(user_vars._icons_path_):
        path_utils.makedirs(user_vars._icons_path_)

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

    def get_repository(self):
        if self.prefs_dic[user_vars._repository_]:
            environment.set_repository(self.prefs_dic[user_vars._repository_])
            return 1
        else:
            logger.info("No repository defined")
            return None

    def set_repository(self, repository):
        if (repository is not None) and (repository != ''):
            if tools.is_dbname_safe(repository):
                self.prefs_dic[user_vars._repository_] = repository
                environment.set_repository(self.prefs_dic[user_vars._repository_])
                self.write_prefs_dic()
                return 1
            else:
                logger.warning(f'Please enter a repository name with only lowercase characters, numbers and "_"')
                return None
        else:
            logger.warning(f'Please provide a repository name')
            return None

    def set_team_dns(self, host, port):
        DNS = (host, port)
        if team_client.try_connection(DNS):
            self.prefs_dic[user_vars._team_dns_] = DNS
            self.write_prefs_dic()
            environment.set_team_dns(DNS)
            logger.info("Team DNS modified")
            return 1
        else:
            logger.warning("Can't reach server with this DNS")
            return None

    def get_team_dns(self):
        if self.prefs_dic[user_vars._team_dns_]:
            if team_client.try_connection(self.prefs_dic[user_vars._team_dns_]):
                environment.set_team_dns(self.prefs_dic[user_vars._team_dns_])
                return 1
            else:
                environment.set_team_dns(self.prefs_dic[user_vars._team_dns_])
                logger.info(f"Can't reach team server with this DNS : {self.prefs_dic[user_vars._team_dns_]}")
                return None
        else:
            logger.info("No team DNS set")
            return None

    def set_widget_pos(self, widget_name, pos_dic):
        self.prefs_dic[user_vars._widgets_pos_][widget_name] = pos_dic
        self.write_prefs_dic()

    def get_widget_pos(self, widget_name):
        if widget_name in self.prefs_dic[user_vars._widgets_pos_].keys():
            return self.prefs_dic[user_vars._widgets_pos_][widget_name]
        else:
            return None

    def add_context(self, type, context_dic):
        if type not in self.prefs_dic.keys():
            self.prefs_dic[type] = dict()
        self.prefs_dic[type][environment.get_project_name()] = context_dic
        self.write_prefs_dic()

    def get_context(self, type):
        if type not in self.prefs_dic.keys():
            return None
        if environment.get_project_name() in self.prefs_dic[type].keys():
            return self.prefs_dic[type][environment.get_project_name()]
        else:
            return None

    def get_show_whatsnew(self):
        if user_vars._show_whatsnew_ in self.prefs_dic.keys():
            return self.prefs_dic[user_vars._show_whatsnew_]
        else:
            self.set_show_whatsnew(True)
            return True

    def set_show_whatsnew(self, show_whatsnew):
        self.prefs_dic[user_vars._show_whatsnew_] = show_whatsnew
        self.write_prefs_dic()

    def get_show_latest_build(self):
        if user_vars._show_latest_build_ in self.prefs_dic.keys():
            return self.prefs_dic[user_vars._show_latest_build_]
        else:
            self.set_show_latest_build(True)
            return True

    def set_show_latest_build(self, show_latest_build):
        self.prefs_dic[user_vars._show_latest_build_] = show_latest_build
        self.write_prefs_dic()

    def set_local_path(self, path):
        if path != '' and path_utils.isdir(path):
            self.prefs_dic[user_vars._local_path_] = path_utils.clean_path(path)
            self.write_prefs_dic()
            logger.info("Local path modified")
            return 1
        else:
            logger.warning('Please enter a valid local path')
            return None

    def set_reference_auto_update_default(self, auto_update_default=False):
        if user_vars._reference_settings_ not in self.prefs_dic.keys():
            self.prefs_dic[user_vars._reference_settings_] = dict()
        self.prefs_dic[user_vars._reference_settings_]['auto_update_default'] = auto_update_default
        self.write_prefs_dic()

    def get_reference_auto_update_default(self):
        if user_vars._reference_settings_ in self.prefs_dic.keys():
            return self.prefs_dic[user_vars._reference_settings_]['auto_update_default']
        else:
            self.set_reference_auto_update_default()
            return False

    def set_popups_settings(self, enabled=1, duration=3, keep_until_comment=True):
        popups_settings_dic = dict()
        popups_settings_dic['enabled'] = enabled
        popups_settings_dic['duration'] = duration
        popups_settings_dic['keep_until_comment'] = keep_until_comment
        self.prefs_dic[user_vars._popups_settings_] = popups_settings_dic
        self.write_prefs_dic()

    def get_popups_enabled(self):
        return self.prefs_dic[user_vars._popups_settings_]['enabled']

    def get_keep_until_comment(self):
        return self.prefs_dic[user_vars._popups_settings_]['keep_until_comment']

    def get_popups_duration(self):
        return self.prefs_dic[user_vars._popups_settings_]['duration']

    def get_local_path(self):
        return self.prefs_dic[user_vars._local_path_]

    def get_user_build(self):
        if user_vars._user_build_ in self.prefs_dic.keys():
            return self.prefs_dic[user_vars._user_build_]
        else:
            self.set_user_build(None)
            return None

    def set_user_build(self, build):
        self.prefs_dic[user_vars._user_build_] = build
        self.write_prefs_dic()

    def get_user_prefs_dic(self):
        # Read ~/Documents/wizard/prefences.yaml
        # or init it if not found
        # return the preferences dictionnary
        self.user_prefs_file = user_vars._user_prefs_file_
        if not path_utils.isdir(user_vars._user_path_):
            path_utils.mkdir(user_vars._user_path_)
        if not path_utils.isfile(self.user_prefs_file):
            self.prefs_dic = dict()
            self.prefs_dic[user_vars._psql_dns_] = None
            self.prefs_dic[user_vars._repository_] = None
            self.prefs_dic[user_vars._team_dns_] = None
            self.prefs_dic[user_vars._tree_context_] = dict()
            self.prefs_dic[user_vars._tabs_context_] = dict()
            self.prefs_dic[user_vars._versions_context_] = dict()
            self.prefs_dic[user_vars._videos_context_] = dict()
            self.prefs_dic[user_vars._wall_context_] = dict()
            self.prefs_dic[user_vars._asset_tracking_context_] = dict()
            self.prefs_dic[user_vars._console_context_] = dict()
            self.prefs_dic[user_vars._production_manager_context_] = dict()
            self.prefs_dic[user_vars._local_path_] = None
            self.prefs_dic[user_vars._popups_settings_] = dict()
            self.prefs_dic[user_vars._popups_settings_]['enabled'] = 1
            self.prefs_dic[user_vars._popups_settings_]['keep_until_comment'] = True
            self.prefs_dic[user_vars._popups_settings_]['duration'] = 3
            self.prefs_dic[user_vars._reference_settings_] = dict()
            self.prefs_dic[user_vars._reference_settings_]['auto_update_default'] = False

            self.prefs_dic[user_vars._show_whatsnew_] = True
            self.prefs_dic[user_vars._user_build_] = None
            self.prefs_dic[user_vars._widgets_pos_] = dict()
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
        except KeyboardInterrupt:
            logger.warning("Execution manually stopped")
        except:
            logger.error(sys.exc_info()[1])

    def execute_py(self, file):
        # Read a .py file and execute the data
        # with "execute_session()"
        if path_utils.isfile(file):
            with open(file, 'r') as f:
                data = f.read()
            self.execute_session(data)
        else:
            logger.warning(f"{file} doesn't exists")

def log_user(user_name, password):
    if user_name in repository.get_user_names_list():
        user_row = repository.get_user_row_by_name(user_name)
        if tools.decrypt_string(user_row['pass'],
                                password):
            repository.update_current_ip_data('user_id', user_row['id'])
            environment.build_user_env(user_row)
            logger.info(f'{user_name} signed in')
            return 1
        else:
            logger.warning(f'Wrong password for {user_name}')
            return None
    else:
        logger.error(f"{user_name} doesn't exists")
        return None

def disconnect_user():
    repository.update_current_ip_data('user_id', None)
    logger.info('You are now disconnected')

def get_user():
    user_id = repository.get_current_ip_data('user_id')
    if user_id:
        environment.build_user_env(user_row=repository.get_user_data(user_id))
        return 1
    else:
        return None

def log_project(project_name, password, wait_for_restart=False):
    if project_name in repository.get_projects_names_list():
        project_row = repository.get_project_row_by_name(project_name)
        if tools.decrypt_string(project_row['project_password'],
                                password):
            repository.update_current_ip_data('project_id', project_row['id'])
            logger.info(f'Successfully signed in {project_name} project')
            if not wait_for_restart:
                environment.build_project_env(project_name, project_row['project_path'])
                db_utils.modify_db_name('project', project_name)
                project.add_user(repository.get_user_row_by_name(environment.get_user(),
                                                                'id'))
            return 1
        else:
            logger.warning(f'Wrong password for {project_name}')
            return None
    else:
        logger.error(f"{project_name} doesn't exists")
        return None

def log_project_without_cred(project_name):
    if project_name in repository.get_projects_names_list():
        project_row = repository.get_project_row_by_name(project_name)
        repository.update_current_ip_data('project_id', project_row['id'])
        environment.build_project_env(project_name, project_row['project_path'])
        db_utils.modify_db_name('project', project_name)
        logger.info(f'Successfully signed in {project_name} project')
        project.add_user(repository.get_user_row_by_name(environment.get_user(),
                                                            'id'))
        return 1
    else:
        logger.error(f"{project_name} doesn't exists")
        return None


def disconnect_project():
    repository.update_current_ip_data('project_id', None)
    logger.info('Successfully disconnect from project')

def get_project():
    project_id = repository.get_current_ip_data('project_id')
    if project_id:
        project_row = repository.get_project_row(project_id) 
        environment.build_project_env(project_name=project_row['project_name'],
                                        project_path=project_row['project_path'])
        return 1
    else:
        return None