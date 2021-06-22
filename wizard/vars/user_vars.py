# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os

# User constants
_user_path_ = os.path.expanduser('~/Documents/wizard_2/')
_user_prefs_file_ = os.path.join(_user_path_, 'preferences.yaml')
_user_logging_file_ = os.path.join(_user_path_, 'main.log')
_script_path_ = os.path.join(_user_path_, 'script')
_icons_path_ = os.path.join(_user_path_, 'icons')
_session_file_ = os.path.join(_script_path_, 'session.py')

# Dictionary keys
_user_ = 'user'
_project_ = 'project'
_scripts_ = 'scripts'
_psql_dns_ = 'psql_dns'
