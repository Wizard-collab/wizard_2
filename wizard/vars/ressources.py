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

_web_server_url_ = 'http://54.39.96.76/'
_documentation_url_ = _web_server_url_ + 'documentation/'


# Softwares
_maya_ = 'maya'
_guerilla_render_ = 'guerilla_render'
_substance_painter_ = 'substance_painter'
_substance_designer_ = 'substance_designer'
_nuke_ = 'nuke'
_houdini_ = 'houdini'
_blender_ = 'blender'

_available_icons_list_ = []

_ressources_path_ = path_utils.abspath('ressources')
_stylesheet_ = path_utils.join(_ressources_path_, 'stylesheet.css')
_icons_path_ = path_utils.abspath('ressources/icons')
_default_script_shelf_icon_ = path_utils.join(_icons_path_, 'shelf_script.png')
_running_gif_ = path_utils.join(_icons_path_, 'running.gif')
_add_icon_small_ = path_utils.join(_icons_path_, 'add_small.svg')
_add_icon_ = path_utils.join(_icons_path_, 'add_icon.svg')
_add_transparent_icon_ = path_utils.join(
    _icons_path_, 'add_transparent_icon.svg')
_available_icons_list_.append(_add_icon_)
_remove_icon_ = path_utils.join(_icons_path_, 'remove_icon.svg')
_available_icons_list_.append(_remove_icon_)
_folder_icon_small_ = path_utils.join(_icons_path_, 'folder_small.svg')
_folder_transparent_icon_ = path_utils.join(
    _icons_path_, 'folder_transparent.svg')
_folder_icon_ = path_utils.join(_icons_path_, 'folder.svg')
_available_icons_list_.append(_folder_icon_)
_assets_group_icon_ = path_utils.join(_icons_path_, 'assets_groups.svg')
_available_icons_list_.append(_assets_group_icon_)
_search_icon_ = path_utils.join(_icons_path_, 'search_icon.svg')
_available_icons_list_.append(_search_icon_)
_close_icon_ = path_utils.join(_icons_path_, 'close_hover.svg')
_available_icons_list_.append(_close_icon_)
_close_tranparent_icon_ = path_utils.join(_icons_path_, 'close.svg')
_close_thin_icon_ = path_utils.join(_icons_path_, 'close_thin.svg')
_admin_badge_ = path_utils.join(_icons_path_, 'admin_badge.svg')
_available_icons_list_.append(_admin_badge_)
_rigth_arrow_icon_ = path_utils.join(_icons_path_, 'right_arrow.svg')
_rigth_arrow_transparent_icon_ = path_utils.join(
    _icons_path_, 'right_arrow_transparent.svg')
_right_icon_ = path_utils.join(_icons_path_, 'right.svg')
_available_icons_list_.append(_right_icon_)
_left_icon_ = path_utils.join(_icons_path_, 'left.svg')
_available_icons_list_.append(_left_icon_)
_no_screenshot_ = path_utils.join(_icons_path_, 'no_screenshot.svg')
_no_preview_ = path_utils.join(_icons_path_, 'no_preview.svg')
_no_screenshot_small_ = path_utils.join(_icons_path_, 'no_screenshot.svg')
_dragdrop_ = path_utils.join(_icons_path_, 'dragdrop.svg')
_available_icons_list_.append(_dragdrop_)
_file_icon_ = path_utils.join(_icons_path_, 'file.svg')
_available_icons_list_.append(_file_icon_)
_tool_list_view_ = path_utils.join(_icons_path_, 'tool_list_view.svg')
_available_icons_list_.append(_tool_list_view_)
_tool_icon_view_ = path_utils.join(_icons_path_, 'tool_icon_view.svg')
_available_icons_list_.append(_tool_icon_view_)
_tool_duplicate_ = path_utils.join(_icons_path_, 'tool_duplicate.svg')
_available_icons_list_.append(_tool_duplicate_)
_tool_save_ = path_utils.join(_icons_path_, 'tool_save.svg')
_available_icons_list_.append(_tool_save_)
_tool_clear_cache_ = path_utils.join(_icons_path_, 'tool_clear_cache.svg')
_available_icons_list_.append(_tool_clear_cache_)
_tool_add_ = path_utils.join(_icons_path_, 'tool_add.svg')
_available_icons_list_.append(_tool_add_)
_tool_folder_ = path_utils.join(_icons_path_, 'tool_folder.svg')
_available_icons_list_.append(_tool_folder_)
_tool_edit_ = path_utils.join(_icons_path_, 'tool_edit.svg')
_available_icons_list_.append(_tool_edit_)
_tool_archive_ = path_utils.join(_icons_path_, 'tool_archive.svg')
_available_icons_list_.append(_tool_archive_)
_tool_frame_range_ = path_utils.join(_icons_path_, 'frame_range.svg')
_available_icons_list_.append(_tool_frame_range_)
_tool_manually_publish_ = path_utils.join(
    _icons_path_, 'tool_manually_publish.svg')
_available_icons_list_.append(_tool_manually_publish_)
_tool_batch_publish_ = path_utils.join(_icons_path_, 'tool_batch_publish.svg')
_available_icons_list_.append(_tool_batch_publish_)
_tool_batch_camera_ = path_utils.join(_icons_path_, 'tool_batch_camera.svg')
_available_icons_list_.append(_tool_batch_camera_)
_tool_update_ = path_utils.join(_icons_path_, 'tool_update.svg')
_available_icons_list_.append(_tool_update_)
_tool_comment_ = path_utils.join(_icons_path_, 'tool_comment.svg')
_available_icons_list_.append(_tool_comment_)
_tool_video_ = path_utils.join(_icons_path_, 'tool_video.svg')
_available_icons_list_.append(_tool_video_)
_tool_focus_ = path_utils.join(_icons_path_, 'tool_focus.svg')
_available_icons_list_.append(_tool_focus_)
_tool_error_ = path_utils.join(_icons_path_, 'tool_error.svg')
_available_icons_list_.append(_tool_error_)
_random_icon_ = path_utils.join(_icons_path_, 'random.svg')
_available_icons_list_.append(_random_icon_)
_bulb_icon_ = path_utils.join(_icons_path_, 'bulb.svg')
_available_icons_list_.append(_bulb_icon_)
_info_icon_ = path_utils.join(_icons_path_, 'info.svg')
_available_icons_list_.append(_info_icon_)
_chip_icon_ = path_utils.join(_icons_path_, 'chip_icon.svg')
_available_icons_list_.append(_chip_icon_)
_python_icon_ = path_utils.join(_icons_path_, 'python.svg')
_available_icons_list_.append(_python_icon_)
_console_icon_ = path_utils.join(_icons_path_, 'console.svg')
_available_icons_list_.append(_console_icon_)
_console_warning_icon_ = path_utils.join(_icons_path_, 'console_warning.svg')
_available_icons_list_.append(_console_warning_icon_)
_console_error_icon_ = path_utils.join(_icons_path_, 'console_error.svg')
_available_icons_list_.append(_console_error_icon_)
_console_info_icon_ = path_utils.join(_icons_path_, 'console_info.svg')
_available_icons_list_.append(_console_info_icon_)
_tasks_icon_ = path_utils.join(_icons_path_, 'tasks.svg')
_available_icons_list_.append(_tasks_icon_)
_tasks_process_icon_ = path_utils.join(_icons_path_, 'tasks_process.svg')
_available_icons_list_.append(_tasks_process_icon_)
_tasks_done_icon_ = path_utils.join(_icons_path_, 'tasks_done.svg')
_available_icons_list_.append(_tasks_done_icon_)
_running_softwares_icon_ = path_utils.join(
    _icons_path_, 'running_softwares.svg')
_available_icons_list_.append(_running_softwares_icon_)
_wall_icon_ = path_utils.join(_icons_path_, 'wall.svg')
_available_icons_list_.append(_wall_icon_)
_wall_notification_icon_ = path_utils.join(
    _icons_path_, 'wall_notification.svg')
_available_icons_list_.append(_wall_notification_icon_)
_wizard_icon_ = path_utils.join(_icons_path_, 'wizard_icon.png')
_wizard_setup_icon_ = path_utils.join(_icons_path_, 'wizard_setup.png')
_wizard_ico_ = path_utils.join(_icons_path_, 'wizard_icon.ico')
_init_work_env_info_image_ = path_utils.join(
    _icons_path_, 'init_work_env_info.png')
_no_video_info_image_ = path_utils.join(_icons_path_, 'info_no_video.png')
_add_group_info_image_ = path_utils.join(_icons_path_, 'add_group_info.png')
_select_stage_info_image_ = path_utils.join(
    _icons_path_, 'select_stage_info.png')
_merge_info_image_ = path_utils.join(_icons_path_, 'info_merge.png')
_chill_info_image_ = path_utils.join(_icons_path_, 'info_chill.png')
_empty_info_image_ = path_utils.join(_icons_path_, 'info_empty.png')
_references_info_image_ = path_utils.join(_icons_path_, 'info_references.png')
_lost_info_image_ = path_utils.join(_icons_path_, 'info_lost.png')
_alone_info_ = path_utils.join(_icons_path_, 'info_alone.png')
_nothing_info_ = path_utils.join(_icons_path_, 'info_nothing.png')
_no_connection_info_ = path_utils.join(_icons_path_, 'info_no_connection.svg')
_agreement_icon_ = path_utils.join(_icons_path_, 'agreement.svg')
_available_icons_list_.append(_agreement_icon_)
_messages_icon_ = path_utils.join(_icons_path_, 'messages.svg')
_available_icons_list_.append(_messages_icon_)
_quit_decoration_ = path_utils.join(_icons_path_, 'quit_decoration.svg')
_resize_decoration_ = path_utils.join(_icons_path_, 'resize_decoration.svg')
_minimize_decoration_ = path_utils.join(
    _icons_path_, 'minimize_decoration.svg')
_manual_export_ = path_utils.join(_icons_path_, 'manual_export.svg')
_available_icons_list_.append(_manual_export_)
_gold_icon_ = path_utils.join(_icons_path_, 'gold.png')
_available_icons_list_.append(_gold_icon_)
_silver_icon_ = path_utils.join(_icons_path_, 'silver.png')
_available_icons_list_.append(_silver_icon_)
_bronze_icon_ = path_utils.join(_icons_path_, 'bronze.png')
_available_icons_list_.append(_bronze_icon_)
_ranking_icon_ = path_utils.join(_icons_path_, 'ranking_icon.svg')
_available_icons_list_.append(_ranking_icon_)
_kill_task_icon_ = path_utils.join(_icons_path_, 'kill_task.svg')
_available_icons_list_.append(_kill_task_icon_)
_refresh_icon_ = path_utils.join(_icons_path_, 'refresh_icon.svg')
_available_icons_list_.append(_refresh_icon_)
_team_connection_on_ = path_utils.join(_icons_path_, 'team_connection_on.svg')
_available_icons_list_.append(_team_connection_on_)
_team_connection_off_ = path_utils.join(
    _icons_path_, 'team_connection_off.svg')
_available_icons_list_.append(_team_connection_off_)
_settings_icon_ = path_utils.join(_icons_path_, 'settings.svg')
_available_icons_list_.append(_settings_icon_)
_user_icon_ = path_utils.join(_icons_path_, 'user_icon.svg')
_available_icons_list_.append(_user_icon_)
_save_icon_ = path_utils.join(_icons_path_, 'save.svg')
_available_icons_list_.append(_save_icon_)
_loading_image_ = path_utils.join(_icons_path_, 'loading_image.png')
_state_todo_ = path_utils.join(_icons_path_, 'state_todo.svg')
_available_icons_list_.append(_state_todo_)
_state_wip_ = path_utils.join(_icons_path_, 'state_wip.svg')
_available_icons_list_.append(_state_wip_)
_state_done_ = path_utils.join(_icons_path_, 'state_done.svg')
_available_icons_list_.append(_state_done_)
_state_error_ = path_utils.join(_icons_path_, 'state_error.svg')
_available_icons_list_.append(_state_error_)
_state_rtk_ = path_utils.join(_icons_path_, 'state_rtk.svg')
_available_icons_list_.append(_state_rtk_)
_state_wfa_ = path_utils.join(_icons_path_, 'state_wfa.svg')
_available_icons_list_.append(_state_wfa_)
_state_omt_ = path_utils.join(_icons_path_, 'state_omt.svg')
_available_icons_list_.append(_state_omt_)
_estimated_time_icon_ = path_utils.join(_icons_path_, 'estimated_time.svg')
_available_icons_list_.append(_estimated_time_icon_)
_work_time_icon_ = path_utils.join(_icons_path_, 'work_time.svg')
_available_icons_list_.append(_work_time_icon_)
_password_visibility_on_ = path_utils.join(
    _icons_path_, 'password_visibility_on.svg')
_password_visibility_off_ = path_utils.join(
    _icons_path_, 'password_visibility_off.svg')
_create_project_image_ = path_utils.join(_icons_path_, 'create_project.svg')
_project_manager_ = path_utils.join(_icons_path_, 'project_manager.svg')
_available_icons_list_.append(_project_manager_)
_create_icon_ = path_utils.join(_icons_path_, 'create.svg')
_available_icons_list_.append(_create_icon_)
_documentation_icon_ = path_utils.join(_icons_path_, 'documentation.svg')
_available_icons_list_.append(_documentation_icon_)
_license_icon_ = path_utils.join(_icons_path_, 'license.svg')
_available_icons_list_.append(_license_icon_)
_dropdown_icon_ = path_utils.join(_icons_path_, 'dropdown.svg')
_dropdown_hover_icon_ = path_utils.join(_icons_path_, 'dropdown_hover.svg')
_production_manager_icon_ = path_utils.join(
    _icons_path_, 'production_manager.svg')
_available_icons_list_.append(_production_manager_icon_)
_videos_manager_icon_ = path_utils.join(_icons_path_, 'videos_manager.svg')
_available_icons_list_.append(_videos_manager_icon_)
_playlist_icon_ = path_utils.join(_icons_path_, 'playlist_icon.svg')
_available_icons_list_.append(_playlist_icon_)
_launch_icon_ = path_utils.join(_icons_path_, 'launch.svg')
_available_icons_list_.append(_launch_icon_)
_isolate_icon_ = path_utils.join(_icons_path_, 'isolate.svg')
_available_icons_list_.append(_isolate_icon_)
_archive_icon_ = path_utils.join(_icons_path_, 'archive.svg')
_available_icons_list_.append(_archive_icon_)
_reduce_icon_ = path_utils.join(_icons_path_, 'reduce.svg')
_available_icons_list_.append(_reduce_icon_)
_expand_icon_ = path_utils.join(_icons_path_, 'expand.svg')
_available_icons_list_.append(_expand_icon_)
_sandbox_icon_ = path_utils.join(_icons_path_, 'sandbox.svg')
_available_icons_list_.append(_sandbox_icon_)
_destination_icon_ = path_utils.join(_icons_path_, 'destination.svg')
_available_icons_list_.append(_destination_icon_)
_edit_icon_ = path_utils.join(_icons_path_, 'edit_hover.svg')
_available_icons_list_.append(_edit_icon_)
_separator_icon_ = path_utils.join(_icons_path_, 'separator_icon.svg')
_available_icons_list_.append(_separator_icon_)
_congrats_icon_ = path_utils.join(_icons_path_, 'congrats.svg')
_available_icons_list_.append(_congrats_icon_)
_guess_icon_ = path_utils.join(_icons_path_, 'guess.svg')
_available_icons_list_.append(_guess_icon_)
_edit_transparent_icon_ = path_utils.join(_icons_path_, 'edit.svg')
_whatsnew_icon_ = path_utils.join(_icons_path_, 'whatsnew.svg')
_available_icons_list_.append(_whatsnew_icon_)
_crash_icon_ = path_utils.join(_icons_path_, 'crash.svg')
_available_icons_list_.append(_crash_icon_)
_send_icon_ = path_utils.join(_icons_path_, 'send.svg')
_available_icons_list_.append(_send_icon_)
_play_icon_ = path_utils.join(_icons_path_, 'play.svg')
_available_icons_list_.append(_play_icon_)
_plug_icon_ = path_utils.join(_icons_path_, 'plug.svg')
_available_icons_list_.append(_plug_icon_)
_hook_icon_ = path_utils.join(_icons_path_, 'hook.svg')
_available_icons_list_.append(_hook_icon_)
_group_icon_ = path_utils.join(_icons_path_, 'group.svg')
_available_icons_list_.append(_group_icon_)
_default_export_version_icon_ = path_utils.join(
    _icons_path_, 'default_export_version.svg')
_available_icons_list_.append(_default_export_version_icon_)
_check_icon_ = path_utils.join(_icons_path_, 'checkBox.svg')
_available_icons_list_.append(_check_icon_)
_uncheck_icon_ = path_utils.join(_icons_path_, 'unchecked.svg')
_star_icon_ = path_utils.join(_icons_path_, 'star.svg')
_available_icons_list_.append(_star_icon_)
_quote_icon_ = path_utils.join(_icons_path_, 'quote.svg')
_available_icons_list_.append(_quote_icon_)
_table_viewer_icon_ = path_utils.join(_icons_path_, 'table_viewer.svg')
_available_icons_list_.append(_table_viewer_icon_)
_red_item_icon_ = path_utils.join(_icons_path_, 'red.png')
_available_icons_list_.append(_red_item_icon_)
_green_item_icon_ = path_utils.join(_icons_path_, 'green.png')
_available_icons_list_.append(_green_item_icon_)
_yellow_item_icon_ = path_utils.join(_icons_path_, 'yellow.png')
_available_icons_list_.append(_yellow_item_icon_)
_skull_item_icon_ = path_utils.join(_icons_path_, 'skull.png')
_available_icons_list_.append(_skull_item_icon_)
_chart_icon_ = path_utils.join(_icons_path_, 'chart_icon.svg')
_available_icons_list_.append(_chart_icon_)
_missing_image_ = path_utils.join(_icons_path_, 'missing_image.svg')
_available_icons_list_.append(_missing_image_)
_update_icon_ = path_utils.join(_icons_path_, 'update_icon.svg')
_available_icons_list_.append(_update_icon_)
_tag_icon_ = path_utils.join(_icons_path_, 'tag.svg')
_available_icons_list_.append(_tag_icon_)
_artefacts_icon_ = path_utils.join(_icons_path_, 'artefacts_icon.svg')
_available_icons_list_.append(_artefacts_icon_)
_potion_red_icon_ = path_utils.join(_icons_path_, 'potion_red.png')
_available_icons_list_.append(_potion_red_icon_)
_potion_green_icon_ = path_utils.join(_icons_path_, 'potion_green.png')
_available_icons_list_.append(_potion_green_icon_)
_potion_blue_icon_ = path_utils.join(_icons_path_, 'potion_blue.png')
_available_icons_list_.append(_potion_blue_icon_)
_potion_2_blue_icon_ = path_utils.join(_icons_path_, 'potion_2_blue.png')
_available_icons_list_.append(_potion_2_blue_icon_)
_potion_2_pink_icon_ = path_utils.join(_icons_path_, 'potion_2_pink.png')
_available_icons_list_.append(_potion_2_pink_icon_)
_steak_icon_ = path_utils.join(_icons_path_, 'steak.png')
_available_icons_list_.append(_steak_icon_)
_book_red_icon_ = path_utils.join(_icons_path_, 'book_red.png')
_available_icons_list_.append(_book_red_icon_)
_book_purple_icon_ = path_utils.join(_icons_path_, 'book_purple.png')
_available_icons_list_.append(_book_purple_icon_)
_mushroom_blue_icon_ = path_utils.join(_icons_path_, 'mushroom_blue.png')
_available_icons_list_.append(_mushroom_blue_icon_)
_mushroom_orange_icon_ = path_utils.join(_icons_path_, 'mushroom_orange.png')
_available_icons_list_.append(_mushroom_orange_icon_)
_ring_green_icon_ = path_utils.join(_icons_path_, 'ring_green.png')
_available_icons_list_.append(_ring_green_icon_)
_ring_blue_icon_ = path_utils.join(_icons_path_, 'ring_blue.png')
_available_icons_list_.append(_ring_blue_icon_)
_shield_icon_ = path_utils.join(_icons_path_, 'shield.png')
_available_icons_list_.append(_shield_icon_)
_coin_icon_ = path_utils.join(_icons_path_, 'coin.png')
_available_icons_list_.append(_coin_icon_)
_coins_1_icon_ = path_utils.join(_icons_path_, 'coins_1.png')
_available_icons_list_.append(_coins_1_icon_)
_coins_2_icon_ = path_utils.join(_icons_path_, 'coins_2.png')
_available_icons_list_.append(_coins_2_icon_)
_apple_icon_ = path_utils.join(_icons_path_, 'apple.png')
_available_icons_list_.append(_apple_icon_)
_chicken_icon_ = path_utils.join(_icons_path_, 'chicken.png')
_available_icons_list_.append(_chicken_icon_)
_thief_icon_ = path_utils.join(_icons_path_, 'thief.png')
_available_icons_list_.append(_thief_icon_)
_beer_icon_ = path_utils.join(_icons_path_, 'beer.png')
_available_icons_list_.append(_beer_icon_)
_sword_icon_ = path_utils.join(_icons_path_, 'sword.png')
_available_icons_list_.append(_sword_icon_)
_heart_icon_ = path_utils.join(_icons_path_, 'heart.png')
_available_icons_list_.append(_heart_icon_)
_level_icon_ = path_utils.join(_icons_path_, 'level.png')
_available_icons_list_.append(_level_icon_)
_purse_icon_ = path_utils.join(_icons_path_, 'purse.png')
_available_icons_list_.append(_purse_icon_)
_market_icon_ = path_utils.join(_icons_path_, 'market.png')
_available_icons_list_.append(_market_icon_)
_batcher_icon_ = path_utils.join(_icons_path_, 'batcher_icon.svg')
_available_icons_list_.append(_batcher_icon_)
_assembly_icon_ = path_utils.join(_icons_path_, 'assembly_icon.svg')
_available_icons_list_.append(_assembly_icon_)
_calendar_icon_ = path_utils.join(_icons_path_, 'calendar_icon.svg')
_available_icons_list_.append(_calendar_icon_)
_move_icon_ = path_utils.join(_icons_path_, 'move_icon.svg')
_available_icons_list_.append(_move_icon_)
_attacks_history_icon_ = path_utils.join(_icons_path_, 'attack_history.png')
_available_icons_list_.append(_attacks_history_icon_)
_key_icon_ = path_utils.join(_icons_path_, 'key.png')
_available_icons_list_.append(_key_icon_)
_filter_icon_ = path_utils.join(_icons_path_, 'filter_icon.svg')
_available_icons_list_.append(_filter_icon_)
_frame_icon_ = path_utils.join(_icons_path_, 'frame_icon.svg')
_available_icons_list_.append(_frame_icon_)
_render_node_icon_ = path_utils.join(_icons_path_, 'render_node_icon.svg')
_available_icons_list_.append(_render_node_icon_)
_render_time_icon_ = path_utils.join(_icons_path_, 'render_time_icon.svg')
_available_icons_list_.append(_render_time_icon_)
_up_arrow_ = path_utils.join(_icons_path_, 'up_arrow.svg')
_available_icons_list_.append(_up_arrow_)
_down_arrow_ = path_utils.join(_icons_path_, 'down_arrow.svg')
_available_icons_list_.append(_down_arrow_)

_pan_icon_ = path_utils.join(_icons_path_, 'pan_icon.svg')
_available_icons_list_.append(_pan_icon_)
_zoom_icon_ = path_utils.join(_icons_path_, 'zoom_icon.svg')
_available_icons_list_.append(_zoom_icon_)
_zoom_vertical_icon_ = path_utils.join(_icons_path_, 'zoom_vertical_icon.svg')
_available_icons_list_.append(_zoom_vertical_icon_)
_zoom_horizontal_icon_ = path_utils.join(
    _icons_path_, 'zoom_horizontal_icon.svg')
_available_icons_list_.append(_zoom_horizontal_icon_)
_focus_icon_ = path_utils.join(_icons_path_, 'focus_icon.svg')
_available_icons_list_.append(_focus_icon_)

_player_play_icon_hover_ = path_utils.join(
    _icons_path_, 'player_play_icon_hover.svg')
_available_icons_list_.append(_player_play_icon_hover_)
_player_play_icon_ = path_utils.join(_icons_path_, 'player_play_icon.svg')
_available_icons_list_.append(_player_play_icon_)
_player_pause_icon_hover_ = path_utils.join(
    _icons_path_, 'player_pause_icon_hover.svg')
_available_icons_list_.append(_player_pause_icon_hover_)
_player_pause_icon_ = path_utils.join(_icons_path_, 'player_pause_icon.svg')
_available_icons_list_.append(_player_pause_icon_)
_player_previous_icon_hover_ = path_utils.join(
    _icons_path_, 'player_previous_icon_hover.svg')
_available_icons_list_.append(_player_previous_icon_hover_)
_player_previous_icon_ = path_utils.join(
    _icons_path_, 'player_previous_icon.svg')
_available_icons_list_.append(_player_previous_icon_)
_player_next_icon_hover_ = path_utils.join(
    _icons_path_, 'player_next_icon_hover.svg')
_available_icons_list_.append(_player_next_icon_hover_)
_player_next_icon_ = path_utils.join(_icons_path_, 'player_next_icon.svg')
_available_icons_list_.append(_player_next_icon_)
_player_end_icon_hover_ = path_utils.join(
    _icons_path_, 'player_end_icon_hover.svg')
_available_icons_list_.append(_player_end_icon_hover_)
_player_end_icon_ = path_utils.join(_icons_path_, 'player_end_icon.svg')
_available_icons_list_.append(_player_end_icon_)
_player_beginning_icon_hover_ = path_utils.join(
    _icons_path_, 'player_beginning_icon_hover.svg')
_available_icons_list_.append(_player_beginning_icon_hover_)
_player_beginning_icon_ = path_utils.join(
    _icons_path_, 'player_beginning_icon.svg')
_available_icons_list_.append(_player_beginning_icon_)
_player_loop_icon_ = path_utils.join(_icons_path_, 'player_loop_icon.svg')
_available_icons_list_.append(_player_loop_icon_)
_player_loop_icon_hover_ = path_utils.join(
    _icons_path_, 'player_loop_icon_hover.svg')
_available_icons_list_.append(_player_loop_icon_hover_)
_player_loop_icon_checked_ = path_utils.join(
    _icons_path_, 'player_loop_icon_checked.svg')
_available_icons_list_.append(_player_loop_icon_checked_)

_important_icon_ = path_utils.join(_icons_path_, 'important.svg')
_available_icons_list_.append(_important_icon_)
_urgent_icon_ = path_utils.join(_icons_path_, 'urgent.svg')
_available_icons_list_.append(_urgent_icon_)

_references_icon_ = path_utils.join(_icons_path_, 'reference_icon.svg')
_work_icon_ = path_utils.join(_icons_path_, 'work_icon.svg')
_exports_icon_ = path_utils.join(_icons_path_, 'export_icon.svg')
_videos_icon_ = path_utils.join(_icons_path_, 'video_icon.svg')

# Lock icons
_lock_icons_ = dict()
_lock_icons_[1] = path_utils.join(_icons_path_, 'locked.svg')
_lock_icons_[0] = path_utils.join(_icons_path_, 'unlocked.svg')

# Domains icons
_assets_icon_ = path_utils.join(_icons_path_, 'assets.svg')
_library_icon_ = path_utils.join(_icons_path_, 'library.svg')
_sequences_icon_ = path_utils.join(_icons_path_, 'sequences.svg')
_domains_icons_dic_ = dict()
_domains_icons_dic_['assets'] = _assets_icon_
_domains_icons_dic_['library'] = _library_icon_
_domains_icons_dic_['sequences'] = _sequences_icon_

# Stages icons
_modeling_icon_ = path_utils.join(_icons_path_, 'modeling.svg')
_rigging_icon_ = path_utils.join(_icons_path_, 'rigging.svg')
_grooming_icon_ = path_utils.join(_icons_path_, 'grooming.svg')
_texturing_icon_ = path_utils.join(_icons_path_, 'texturing.svg')
_shading_icon_ = path_utils.join(_icons_path_, 'shading.svg')
_available_icons_list_.append(_modeling_icon_)
_available_icons_list_.append(_rigging_icon_)
_available_icons_list_.append(_grooming_icon_)
_available_icons_list_.append(_texturing_icon_)
_available_icons_list_.append(_shading_icon_)

_layout_icon_ = path_utils.join(_icons_path_, 'layout.svg')
_animation_icon_ = path_utils.join(_icons_path_, 'animation.svg')
_cfx_icon_ = path_utils.join(_icons_path_, 'cfx.svg')
_fx_icon_ = path_utils.join(_icons_path_, 'fx.svg')
_lighting_icon_ = path_utils.join(_icons_path_, 'lighting.svg')
_rendering_icon_ = path_utils.join(_icons_path_, 'rendering.svg')
_compositing_icon_ = path_utils.join(_icons_path_, 'compositing.svg')
_camera_icon_ = path_utils.join(_icons_path_, 'camera.svg')
_available_icons_list_.append(_layout_icon_)
_available_icons_list_.append(_animation_icon_)
_available_icons_list_.append(_cfx_icon_)
_available_icons_list_.append(_fx_icon_)
_available_icons_list_.append(_lighting_icon_)
_available_icons_list_.append(_compositing_icon_)
_available_icons_list_.append(_camera_icon_)

_custom_icon_ = path_utils.join(_icons_path_, 'custom.svg')
_available_icons_list_.append(_custom_icon_)
_camera_rig_icon_ = path_utils.join(_icons_path_, 'camera_rig.svg')
_available_icons_list_.append(_camera_rig_icon_)

_stage_icons_dic_ = dict()
_stage_icons_dic_['modeling'] = _modeling_icon_
_stage_icons_dic_['rigging'] = _rigging_icon_
_stage_icons_dic_['grooming'] = _grooming_icon_
_stage_icons_dic_['texturing'] = _texturing_icon_
_stage_icons_dic_['shading'] = _shading_icon_
_stage_icons_dic_['layout'] = _layout_icon_
_stage_icons_dic_['animation'] = _animation_icon_
_stage_icons_dic_['cfx'] = _cfx_icon_
_stage_icons_dic_['fx'] = _fx_icon_
_stage_icons_dic_['lighting'] = _lighting_icon_
_stage_icons_dic_['rendering'] = _rendering_icon_
_stage_icons_dic_['compositing'] = _compositing_icon_
_stage_icons_dic_['camera'] = _camera_icon_
_stage_icons_dic_['custom'] = _custom_icon_
_stage_icons_dic_['camrig'] = _camera_rig_icon_

# Softwares icons
_softwares_icons_dic_ = dict()
_softwares_icons_dic_[_maya_] = path_utils.join(_icons_path_, 'maya.svg')
_softwares_icons_dic_[_guerilla_render_] = path_utils.join(
    _icons_path_, 'guerilla_render.svg')
_softwares_icons_dic_[_substance_painter_] = path_utils.join(
    _icons_path_, 'substance_painter.svg')
_softwares_icons_dic_[_substance_designer_] = path_utils.join(
    _icons_path_, 'substance_designer.svg')
_softwares_icons_dic_[_nuke_] = path_utils.join(_icons_path_, 'nuke.svg')
_softwares_icons_dic_[_houdini_] = path_utils.join(_icons_path_, 'houdini.svg')
_softwares_icons_dic_[_blender_] = path_utils.join(_icons_path_, 'blender.svg')
for key in _softwares_icons_dic_.keys():
    _available_icons_list_.append(_softwares_icons_dic_[key])

# Domains colors
_domains_colors_ = dict()
_domains_colors_['assets'] = '#fb7771'
_domains_colors_['library'] = '#edd753'
_domains_colors_['sequences'] = '#90cc72'

# Production manager colors
_states_colors_ = dict()
_states_colors_['todo'] = '#3a3a41'
_states_colors_['wip'] = '#b6864e'
_states_colors_['done'] = '#7ca657'
_states_colors_['error'] = '#d16666'
_states_colors_['rtk'] = '#4768b5'
_states_colors_['wfa'] = '#8047b5'
_states_colors_['omt'] = '#2e2e2e'

_states_icons_ = dict()
_states_icons_['todo'] = _state_todo_
_states_icons_['wip'] = _state_wip_
_states_icons_['done'] = _state_done_
_states_icons_['error'] = _state_error_
_states_icons_['rtk'] = _state_rtk_
_states_icons_['wfa'] = _state_wfa_
_states_icons_['omt'] = _state_omt_

_stages_colors_ = dict()
_stages_colors_['modeling'] = '#f87474'
_stages_colors_['rigging'] = '#ffb562'
_stages_colors_['grooming'] = '#9eb23b'
_stages_colors_['texturing'] = '#fe83c6'
_stages_colors_['shading'] = '#e168ff'

_stages_colors_['layout'] = '#3ab0ff'
_stages_colors_['animation'] = '#fee440'
_stages_colors_['cfx'] = '#865439'
_stages_colors_['fx'] = '#4b8673'
_stages_colors_['camera'] = '#94b49f'
_stages_colors_['custom'] = '#94b49f'
_stages_colors_['camrig'] = '#94b49f'
_stages_colors_['lighting'] = '#63f191'
_stages_colors_['rendering'] = '#63f191'
_stages_colors_['compositing'] = '#676fa3'

_whatsnew_yaml_ = path_utils.join(_ressources_path_, 'whatsnew.yaml')

# Urgence icons
_priority_icons_list_ = dict()
_priority_icons_list_['normal'] = ''
_priority_icons_list_['high'] = _important_icon_
_priority_icons_list_['urgent'] = _urgent_icon_
