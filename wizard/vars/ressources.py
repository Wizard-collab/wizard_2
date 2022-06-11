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

_documentation_url_ = 'http://93.19.210.30/Documentation/build/html/index.html'

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
_icons_path_ = path_utils.abspath('ressources/icons')
_default_script_shelf_icon_ = path_utils.join(_icons_path_, 'shelf_script.png')
_running_gif_ = path_utils.join(_icons_path_, 'running.gif')
_add_icon_small_ = path_utils.join(_icons_path_, 'add_small.svg')
_add_icon_ = path_utils.join(_icons_path_, 'add_icon.svg')
_add_transparent_icon_ = path_utils.join(_icons_path_, 'add_transparent_icon.svg')
_available_icons_list_.append(_add_icon_)
_folder_icon_small_ = path_utils.join(_icons_path_, 'folder_small.svg')
_folder_transparent_icon_ = path_utils.join(_icons_path_, 'folder_transparent.svg')
_folder_icon_ = path_utils.join(_icons_path_, 'folder.svg')
_available_icons_list_.append(_folder_icon_)
_search_icon_ = path_utils.join(_icons_path_, 'search_icon.svg')
_available_icons_list_.append(_search_icon_)
_close_icon_ = path_utils.join(_icons_path_, 'close_hover.svg')
_available_icons_list_.append(_close_icon_)
_close_tranparent_icon_ = path_utils.join(_icons_path_, 'close.svg')
_close_thin_icon_ = path_utils.join(_icons_path_, 'close_thin.svg')
_admin_badge_ = path_utils.join(_icons_path_, 'admin_badge.svg')
_available_icons_list_.append(_admin_badge_)
_rigth_arrow_icon_ = path_utils.join(_icons_path_, 'right_arrow.svg')
_rigth_arrow_transparent_icon_ = path_utils.join(_icons_path_, 'right_arrow_transparent.svg')
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
_tool_add_ = path_utils.join(_icons_path_, 'tool_add.svg')
_available_icons_list_.append(_tool_add_)
_tool_folder_ = path_utils.join(_icons_path_, 'tool_folder.svg')
_available_icons_list_.append(_tool_folder_)
_tool_edit_ = path_utils.join(_icons_path_, 'tool_edit.svg')
_available_icons_list_.append(_tool_edit_)
_tool_archive_ = path_utils.join(_icons_path_, 'tool_archive.svg')
_available_icons_list_.append(_tool_archive_)
_tool_manually_publish_ = path_utils.join(_icons_path_, 'tool_manually_publish.svg')
_available_icons_list_.append(_tool_manually_publish_)
_tool_batch_publish_ = path_utils.join(_icons_path_, 'tool_batch_publish.svg')
_available_icons_list_.append(_tool_batch_publish_)
_tool_batch_camera_ = path_utils.join(_icons_path_, 'tool_batch_camera.svg')
_available_icons_list_.append(_tool_batch_camera_)
_tool_update_ = path_utils.join(_icons_path_, 'tool_update.svg')
_available_icons_list_.append(_tool_update_)
_tool_comment_ = path_utils.join(_icons_path_, 'tool_comment.svg')
_available_icons_list_.append(_tool_comment_)
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
_running_softwares_icon_ = path_utils.join(_icons_path_, 'running_softwares.svg')
_available_icons_list_.append(_running_softwares_icon_)
_wall_icon_ = path_utils.join(_icons_path_, 'wall.svg')
_available_icons_list_.append(_wall_icon_)
_wall_notification_icon_ = path_utils.join(_icons_path_, 'wall_notification.svg')
_available_icons_list_.append(_wall_notification_icon_)
_wizard_icon_ = path_utils.join(_icons_path_, 'wizard_icon.svg')
_wizard_ico_ = path_utils.join(_icons_path_, 'wizard_icon.ico')
_init_work_env_info_image_ = path_utils.join(_icons_path_, 'init_work_env_info.png')
_add_group_info_image_ = path_utils.join(_icons_path_, 'add_group_info.png')
_select_stage_info_image_ = path_utils.join(_icons_path_, 'select_stage_info.png')
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
_minimize_decoration_ = path_utils.join(_icons_path_, 'minimize_decoration.svg')
_manual_export_ = path_utils.join(_icons_path_, 'manual_export.svg')
_available_icons_list_.append(_manual_export_)
_gold_icon_ = path_utils.join(_icons_path_, 'gold.svg')
_available_icons_list_.append(_gold_icon_)
_silver_icon_ = path_utils.join(_icons_path_, 'silver.svg')
_available_icons_list_.append(_silver_icon_)
_bronze_icon_ = path_utils.join(_icons_path_, 'bronze.svg')
_available_icons_list_.append(_bronze_icon_)
_ranking_icon_ = path_utils.join(_icons_path_, 'ranking_icon.svg')
_available_icons_list_.append(_ranking_icon_)
_kill_task_icon_ = path_utils.join(_icons_path_, 'kill_task.svg')
_available_icons_list_.append(_kill_task_icon_)
_refresh_icon_ = path_utils.join(_icons_path_, 'refresh_icon.svg')
_available_icons_list_.append(_refresh_icon_)
_team_connection_on_ = path_utils.join(_icons_path_, 'team_connection_on.svg')
_available_icons_list_.append(_team_connection_on_)
_team_connection_off_ = path_utils.join(_icons_path_, 'team_connection_off.svg')
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
_estimated_time_icon_ = path_utils.join(_icons_path_, 'estimated_time.svg')
_available_icons_list_.append(_estimated_time_icon_)
_work_time_icon_ = path_utils.join(_icons_path_, 'work_time.svg')
_available_icons_list_.append(_work_time_icon_)
_password_visibility_on_ = path_utils.join(_icons_path_, 'password_visibility_on.svg')
_password_visibility_off_ = path_utils.join(_icons_path_, 'password_visibility_off.svg')
_create_project_image_ = path_utils.join(_icons_path_, 'create_project.svg')
_project_manager_ = path_utils.join(_icons_path_, 'project_manager.svg')
_available_icons_list_.append(_project_manager_)
_create_icon_ =  path_utils.join(_icons_path_, 'create.svg')
_available_icons_list_.append(_create_icon_)
_documentation_icon_ =  path_utils.join(_icons_path_, 'documentation.svg')
_available_icons_list_.append(_documentation_icon_)
_license_icon_ =  path_utils.join(_icons_path_, 'license.svg')
_available_icons_list_.append(_license_icon_)
_dropdown_icon_ =  path_utils.join(_icons_path_, 'dropdown.svg')
_dropdown_hover_icon_ =  path_utils.join(_icons_path_, 'dropdown_hover.svg')
_production_manager_icon_ =  path_utils.join(_icons_path_, 'production_manager.svg')
_available_icons_list_.append(_production_manager_icon_)
_launch_icon_ = path_utils.join(_icons_path_, 'launch.svg')
_available_icons_list_.append(_launch_icon_)
_isolate_icon_ = path_utils.join(_icons_path_, 'isolate.svg')
_available_icons_list_.append(_isolate_icon_)
_archive_icon_ = path_utils.join(_icons_path_, 'archive.svg')
_available_icons_list_.append(_archive_icon_)
_reduce_icon_ = path_utils.join(_icons_path_, 'reduce.svg')
_available_icons_list_.append(_reduce_icon_)
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
_default_export_version_icon_ = path_utils.join(_icons_path_, 'default_export_version.svg')
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

_references_icon_ = path_utils.join(_icons_path_, 'reference_icon.svg')
_work_icon_ = path_utils.join(_icons_path_, 'work_icon.svg')
_exports_icon_ = path_utils.join(_icons_path_, 'export_icon.svg')

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
_stage_icons_dic_['compositing'] = _compositing_icon_
_stage_icons_dic_['camera'] = _camera_icon_
_stage_icons_dic_['custom'] = _custom_icon_
_stage_icons_dic_['camrig'] = _camera_rig_icon_

# Softwares icons
_sofwares_icons_dic_ = dict()
_sofwares_icons_dic_[_maya_] = path_utils.join(_icons_path_, 'maya.svg')
_sofwares_icons_dic_[_guerilla_render_] = path_utils.join(_icons_path_, 'guerilla_render.svg')
_sofwares_icons_dic_[_substance_painter_] = path_utils.join(_icons_path_, 'substance_painter.svg')
_sofwares_icons_dic_[_substance_designer_] = path_utils.join(_icons_path_, 'substance_designer.svg')
_sofwares_icons_dic_[_nuke_] = path_utils.join(_icons_path_, 'nuke.svg')
_sofwares_icons_dic_[_houdini_] = path_utils.join(_icons_path_, 'houdini.svg')
_sofwares_icons_dic_[_blender_] = path_utils.join(_icons_path_, 'blender.svg')
for key in _sofwares_icons_dic_.keys():
	_available_icons_list_.append(_sofwares_icons_dic_[key])
