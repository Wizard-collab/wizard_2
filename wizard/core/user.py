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
from wizard.core.project import project
from wizard.core.site import site

from wizard.core import logging
logging = logging.get_logger(__name__)

def create_user_folders():
    if not os.path.isdir(user_vars._script_path_):
        os.mkdir(user_vars._script_path_)
    sys.path.append(user_vars._script_path_)
    if not os.path.isdir(user_vars._icons_path_):
        os.mkdir(user_vars._icons_path_)

def init_user_session():
    with open(user_vars._session_file_, 'w') as f:
        f.write('')

create_user_folders()
init_user_session()

import session

class user:
    def __init__(self):
        self.get_user_prefs_dic()
    
    def get_site_path(self):
        site_path = self.prefs_dic[user_vars._site_path_]
        if site_path:
            environment.build_site_env(site_path)
            site().add_ip_user()
            return 1
        else:
            return None

    def set_site_path(self, site_path):
        self.prefs_dic[user_vars._site_path_] = site_path
        self.write_prefs_dic()
        environment.build_site_env(site_path)
        site().add_ip_user()

    def add_shelf_script(self,
                            name,
                            py_file,
                            only_subprocess=0,
                            icon=ressources._default_script_shelf_icon_):
        if name not in self.prefs_dic[user_vars._scripts_].keys():
            if not os.path.isfile(icon):
                logging.warning(f"{icon} doesn't exists, assigning default icon")
                icon = ressources._default_script_shelf_icon_
            icon_name = os.path.basename(icon)
            destination_icon = os.path.join(user_vars._icons_path_, icon_name)
            icon_file = tools.get_filename_without_override(destination_icon)
            with open(icon_file, 'wb') as f:
                f.write(image.convert_image_to_bytes(icon))
            self.prefs_dic[user_vars._scripts_][name]=dict()
            self.prefs_dic[user_vars._scripts_][name]['name'] = name
            self.prefs_dic[user_vars._scripts_][name]['py_file'] = py_file
            self.prefs_dic[user_vars._scripts_][name]['only_subprocess'] = only_subprocess
            self.prefs_dic[user_vars._scripts_][name]['icon'] = icon_file
            self.write_prefs_dic()
            logging.info("Shelf script created")
            return 1
        else:
            logging.warning(f"{name} already exists")
            return 0

    def get_shelf_script_data(self, name, data=None):
        if name in self.prefs_dic[user_vars._scripts_].keys():
            script_dic = self.prefs_dic[user_vars._scripts_][name]
            icon = self.prefs_dic[user_vars._scripts_][name]['icon']
            if not os.path.isfile(icon):
                icon = ressources._default_script_shelf_icon_
            image_bytes = image.convert_image_to_bytes(icon)
            self.prefs_dic[user_vars._scripts_][name]['icon'] = image_bytes
            if data:
                if data in self.prefs_dic[user_vars._scripts_][name].keys():
                    return self.prefs_dic[user_vars._scripts_][name][data]
                else:
                    logging.warning(f"{data} column doesn't seems to exists")
            else:
                return self.prefs_dic[user_vars._scripts_][name]
        else:
            logging.warning(f"Script {name} not found")
            return None

    def get_user_prefs_dic(self):
        self.user_prefs_file = user_vars._user_prefs_file_
        if not os.path.isdir(user_vars._user_path_):
            os.mkdir(user_vars._user_path_)
        if not os.path.isfile(self.user_prefs_file):
            self.prefs_dic = dict()
            self.prefs_dic[user_vars._site_path_] = None
            self.prefs_dic[user_vars._scripts_] = dict()
            self.write_prefs_dic()
        else:
            with open(self.user_prefs_file, 'r') as f:
                self.prefs_dic = yaml.load(f, Loader=yaml.Loader)

    def write_prefs_dic(self):
        with open(self.user_prefs_file, 'w') as f:
            yaml.dump(self.prefs_dic, f)

    def execute_session(self, script):
        with open(user_vars._session_file_, 'w') as f:
                f.write(script)
        importlib.reload(session)

    def execute_py(self, file):
        if os.path.isfile(file):
            with open(file, 'r') as f:
                data = f.read()
            self.execute_session(data)
        else:
            logging.warning(f"{file} doesn't exists")

def log_user(user_name, password):
    site_obj = site()
    if user_name in site_obj.get_user_names_list():
        user_row = site_obj.get_user_row_by_name(user_name)
        if tools.decrypt_string(user_row['pass'],
                                password):
            site().update_current_ip_data('user_id', user_row['id'])
            environment.build_user_env(user_name)
            logging.info(f'{user_name} signed in')
        else:
            logging.warning(f'Wrong password for {user_name}')
    else:
        logging.error(f"{user_name} doesn't exists")

def disconnect_user():
    site().update_current_ip_data('user_id', None)
    logging.info('You are now disconnected')

def get_user():
    user_id = site().get_current_ip_data('user_id')
    if user_id:
        environment.build_user_env(user_name=site().get_user_data(user_id,
                                                                'user_name'))
        return 1
    else:
        return None

def log_project(project_name, password):
    site_obj = site()
    if project_name in site_obj.get_projects_names_list():
        project_row = site_obj.get_project_row_by_name(project_name)
        if tools.decrypt_string(project_row['project_password'],
                                password):
            site().update_current_ip_data('project_id', project_row['id'])
            environment.build_project_env(project_name, project_row['project_path'])
            logging.info(f'Successfully signed in {project_name} project')
            project().add_user(site_obj.get_user_row_by_name(environment.get_user(),
                                                                'id'))
        else:
            logging.warning(f'Wrong password for {project_name}')
    else:
        logging.error(f"{project_name} doesn't exists")

def disconnect_project():
    site().update_current_ip_data('project_id', None)
    logging.info('Successfully disconnect from project')

def get_project():
    project_id = site().get_current_ip_data('project_id')
    if project_id:
        project_row = site().get_project_row(project_id) 
        environment.build_project_env(project_name=project_row['project_name'],
                                        project_path=project_row['project_path'])
        return 1
    else:
        return None