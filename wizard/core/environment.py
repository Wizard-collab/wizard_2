# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module build the wizard environment
# ( Current project and current user )
# It permits to avoid some database access
# during the use of the application

# Pyton modules
import os

# Wizard modules
from wizard.vars import env_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

def build_site_env(site_path):
	os.environ[env_vars._site_path_env_] = site_path
	return 1

def build_user_env(user_name):
	os.environ[env_vars._username_env_] = user_name
	return 1

def build_project_env(project_name, project_path):
	os.environ[env_vars._project_name_env_] = project_name
	os.environ[env_vars._project_path_env_] = project_path
	return 1

def get_user():
	if env_vars._username_env_ in os.environ.keys():
		return os.environ[env_vars._username_env_]
	else:
		logging.error('No user defined')
		return None

def get_site_path():
	if env_vars._site_path_env_ in os.environ.keys():
		return os.environ[env_vars._site_path_env_]
	else:
		logging.error('No site path defined')
		return None

def get_project_name():
	if env_vars._project_name_env_ in os.environ.keys():
		return os.environ[env_vars._project_name_env_]
	else:
		logging.error('No project defined')
		return None

def get_project_path():
	if env_vars._project_path_env_ in os.environ.keys():
		return os.environ[env_vars._project_path_env_]
	else:
		logging.error('No project defined')
		return None