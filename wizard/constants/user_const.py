# coding: utf-8

# Python modules
import os

# User constants
_user_path_ = '{}/Documents/wizard_2/'.format(os.getenv("USERPROFILE"))
_user_prefs_file_ = os.path.join(_user_path_, 'preferences.yaml')

# Dictionarry keys
_site_path_ = 'site_path'
_user_ = 'user'
