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

# Wizard modules
from wizard.core import path_utils

# User constants
_user_path_ = os.path.expanduser('~/Documents/wizard/')
_user_prefs_file_ = path_utils.join(_user_path_, 'preferences.yaml')
_user_logger_file_ = path_utils.join(_user_path_, 'main.log')
_data_collect_file_ = path_utils.join(_user_path_, 'data_collect.json')
_subtasks_logs_ = path_utils.join(_user_path_, 'subtasks_logs')
_script_path_ = path_utils.join(_user_path_, 'script')
_icons_path_ = path_utils.join(_user_path_, 'icons')
_session_file_ = path_utils.join(_script_path_, 'session.py')


# Dictionary keys
_user_ = 'user'
_repository_ = 'repository'
_project_ = 'project'
_scripts_ = 'scripts'
_psql_dns_ = 'psql_dns'
_team_dns_ = 'team_dns'
_main_layout_context_ = 'main_layout_context'
_tree_context_ = 'tree_context'
_tabs_context_ = 'tabs_context'
_versions_context_ = 'versions_context'
_videos_context_ = 'videos_context'
_wall_context_ = 'wall_context'
_asset_tracking_context_ = 'asset_tracking_context'
_console_context_ = 'console_context'
_production_manager_context_ = 'production_manager_context'
_production_table_context_ = 'production_table_context'
_production_calendar_context_ = 'production_calendar_context'
_local_path_ = 'local_path'
_popups_settings_ = 'popups_settings'
_show_splash_screen_ = 'show_splash_screen'
_show_latest_build_ = 'show_latest_build'
_user_build_ = 'user_build'
_creation_items_visibility_ = 'creation_items_visibility'
_widgets_pos_ = 'widgets_pos'
_reference_settings_ = 'references_settings'
_recent_work_envs_ = 'recent_work_envs'
_subtasks_datas_yaml_ = 'subtasks.yaml'
_video_player_context_ = 'video_player_context'
_video_timeline_context_ = 'video_player_context'
_video_browser_context_ = 'video_browser_context'
_playlist_browser_context_ = 'playlist_browser_context'
_video_manager_context_ = 'video_manager_context'
