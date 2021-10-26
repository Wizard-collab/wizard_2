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

# Python modules
import os

# User constants
_user_path_ = os.path.expanduser('~/Documents/wizard_2/')
_user_prefs_file_ = os.path.join(_user_path_, 'preferences.yaml')
_user_logger_file_ = os.path.join(_user_path_, 'main.log')
_subtasks_logs_ = os.path.join(_user_path_, 'subtasks_logs')
_script_path_ = os.path.join(_user_path_, 'script')
_icons_path_ = os.path.join(_user_path_, 'icons')
_session_file_ = os.path.join(_script_path_, 'session.py')

# Dictionary keys
_user_ = 'user'
_project_ = 'project'
_scripts_ = 'scripts'
_psql_dns_ = 'psql_dns'
_team_dns_ = 'team_dns'
_tree_context_ = 'tree_context'
_tabs_context_ = 'tabs_context'
_versions_context_ = 'versions_context'
_wall_context_ = 'wall_context'
_asset_tracking_context_ = 'asset_tracking_context'
_console_context_ = 'console_context'
_tickets_context_ = 'tickets_context'
_local_path_ = 'local_path'
_popups_settings_ = 'popups_settings'
