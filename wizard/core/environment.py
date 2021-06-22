# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module build the wizard environment
# ( Current project and current user )
# It permits to avoid some database access
# during the use of the application

# Pyton modules
import os
import json

# Wizard modules
from wizard.vars import env_vars

from wizard.core import logging
logging = logging.get_logger(__name__)

def build_user_env(user_name):
	os.environ[env_vars._username_env_] = user_name
	return 1

def build_project_env(project_name, project_path):
	os.environ[env_vars._project_name_env_] = project_name
	os.environ[env_vars._project_path_env_] = project_path
	return 1

def set_psql_dns(DNS):
	os.environ[env_vars._psql_dns_] = DNS
	return 1

def get_psql_dns():
	if env_vars._psql_dns_ in os.environ.keys():
		return os.environ[env_vars._psql_dns_]
	else:
		logging.error('No PostgreSQL DNS defined')
		return None

def add_running_work_env(work_env_id):
	if env_vars._running_work_envs_ not in os.environ.keys():
		os.environ[env_vars._running_work_envs_] = json.dumps([work_env_id])
	else:
		work_env_list = json.loads(os.environ[env_vars._running_work_envs_])
		work_env_list.append(work_env_id)
		os.environ[env_vars._running_work_envs_] = json.dumps(work_env_list)

def remove_running_work_env(work_env_id):
	if env_vars._running_work_envs_ not in os.environ.keys():
		os.environ[env_vars._running_work_envs_] = json.dumps([])
	else:
		work_env_list = json.loads(os.environ[env_vars._running_work_envs_])
		work_env_list.remove(work_env_id)
		os.environ[env_vars._running_work_envs_] = json.dumps(work_env_list)

def get_running_work_envs():
	work_envs_list = []
	if env_vars._running_work_envs_ in os.environ.keys():
		work_envs_list = json.loads(os.environ[env_vars._running_work_envs_])
	return work_envs_list

def get_user():
	if env_vars._username_env_ in os.environ.keys():
		return os.environ[env_vars._username_env_]
	else:
		logging.error('No user defined')
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