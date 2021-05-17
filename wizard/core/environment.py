# coding: utf-8

# Pyton modules
import os

# Wizard modules
from wizard.core import site
from wizard.constants import env_const

from wizard.core import logging
logging = logging.get_logger(__name__)

def build_site_env(site_path):
	if site_path:
		os.environ[env_const._site_path_env_] = site_path
		return 1
	else:
		logging.warning('No site path defined')
		return None

def build_user_env(user_name):
	if user_name:
		os.environ[env_const._username_env_] = user_name
		return 1
	else:
		logging.warning('No user defined')
		return None

def get_user():
	if env_const._username_env_ in os.environ.keys():
		return os.environ[env_const._username_env_]
	else:
		logging.error('No user defined')
		return None

def get_site_path():
	if env_const._site_path_env_ in os.environ.keys():
		return os.environ[env_const._site_path_env_]
	else:
		logging.error('No site path defined')
		return None