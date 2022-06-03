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

# This module build the wizard environment
# ( Current project and current user )
# It permits to avoid some database access
# during the use of the application

# Pyton modules
import os
import json
import logging

# Wizard modules
from wizard.vars import env_vars

logger = logging.getLogger(__name__)

def build_user_env(user_row):
	os.environ[env_vars._username_env_] = user_row['user_name']
	os.environ[env_vars._useremail_env_] = user_row['email']
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
		logger.error('No PostgreSQL DNS defined')
		return None

def set_communicate_server_port(port):
	os.environ[env_vars._communicate_server_port_] = str(port)
	return 1

def set_softwares_server_port(port):
	os.environ[env_vars._softwares_server_port_] = str(port)
	return 1

def get_softwares_server_port():
	if env_vars._softwares_server_port_ in os.environ.keys():
		return int(os.environ[env_vars._softwares_server_port_])
	else:
		logger.error('No softwares server port defined')
		return None

def set_gui_server_port(port):
	os.environ[env_vars._gui_server_port_] = str(port)
	return 1

def get_gui_server_port():
	if env_vars._gui_server_port_ in os.environ.keys():
		return int(os.environ[env_vars._gui_server_port_])
	else:
		logger.debug('No gui server port defined')
		return None

def set_local_db_server_port(port):
	os.environ[env_vars._local_db_server_port_] = str(port)
	return 1

def get_local_db_server_port():
	if env_vars._local_db_server_port_ in os.environ.keys():
		return int(os.environ[env_vars._local_db_server_port_])
	else:
		logger.error('No local db server port defined')
		return None

def set_team_dns(DNS):
	os.environ[env_vars._team_dns_] = json.dumps(DNS)
	return 1

def get_team_dns():
	if env_vars._team_dns_ in os.environ.keys():
		return json.loads(os.environ[env_vars._team_dns_])
	else:
		logger.debug('No team DNS defined')
		return None

def get_user():
	if env_vars._username_env_ in os.environ.keys():
		return os.environ[env_vars._username_env_]
	else:
		logger.error('No user defined')
		return None

def get_user_email():
	if env_vars._useremail_env_ in os.environ.keys():
		return os.environ[env_vars._useremail_env_]
	else:
		logger.error('No user email defined')
		return None

def get_project_name():
	if env_vars._project_name_env_ in os.environ.keys():
		return os.environ[env_vars._project_name_env_]
	else:
		logger.info('No project defined')
		return None

def get_project_path():
	if env_vars._project_path_env_ in os.environ.keys():
		return os.environ[env_vars._project_path_env_]
	else:
		logger.info('No project defined')
		return None

def get_repository():
	if env_vars._repository_env_ in os.environ.keys():
		return os.environ[env_vars._repository_env_]
	else:
		logger.error('No repository defined')
		return None

def set_repository(repository):
	os.environ[env_vars._repository_env_] = f"repository_{repository}"
