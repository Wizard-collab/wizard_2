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

# Softwares
_maya_ = 'maya'
_guerilla_render_ = 'guerilla_render'
_substance_painter_ = 'substance_painter'
_substance_designer_ = 'substance_designer'
_nuke_ = 'nuke'
_houdini_ = 'houdini'
_blender_ = 'blender'

_ressources_path_ = os.path.abspath('ressources')
_icons_path_ = os.path.abspath('ressources/icons')
_default_profile_ = os.path.join(_icons_path_, 'default_profile.png')
_default_script_shelf_icon_ = os.path.join(_icons_path_, 'shelf_script.png')
_running_gif_ = os.path.join(_icons_path_, 'running.gif')
_add_icon_small_ = os.path.join(_icons_path_, 'add_small.svg')
_add_icon_ = os.path.join(_icons_path_, 'add_icon.svg')
_folder_icon_small_ = os.path.join(_icons_path_, 'folder_small.svg')
_folder_icon_ = os.path.join(_icons_path_, 'folder.svg')
_search_icon_ = os.path.join(_icons_path_, 'search_icon.svg')
_close_icon_ = os.path.join(_icons_path_, 'close_hover.svg')
_close_tranparent_icon_ = os.path.join(_icons_path_, 'close.svg')
_close_thin_icon_ = os.path.join(_icons_path_, 'close_thin.svg')
_admin_badge_ = os.path.join(_icons_path_, 'admin_badge.svg')
_rigth_arrow_icon_ = os.path.join(_icons_path_, 'right_arrow.svg')
_no_screenshot_ = os.path.join(_icons_path_, 'no_screenshot.svg')
_no_screenshot_small_ = os.path.join(_icons_path_, 'no_screenshot.svg')
_dragdrop_ = os.path.join(_icons_path_, 'dragdrop.svg')
_file_icon_ = os.path.join(_icons_path_, 'file.svg')
_tool_list_view_ = os.path.join(_icons_path_, 'tool_list_view.png')
_tool_icon_view_ = os.path.join(_icons_path_, 'tool_icon_view.png')
_tool_duplicate_ = os.path.join(_icons_path_, 'tool_duplicate.png')
_tool_add_ = os.path.join(_icons_path_, 'tool_add.png')
_tool_folder_ = os.path.join(_icons_path_, 'tool_folder.png')
_tool_archive_ = os.path.join(_icons_path_, 'tool_archive.png')
_tool_manually_publish_ = os.path.join(_icons_path_, 'tool_manually_publish.png')
_tool_batch_publish_ = os.path.join(_icons_path_, 'tool_batch_publish.png')
_tool_launch_ = os.path.join(_icons_path_, 'tool_launch.png')
_tool_ticket_ = os.path.join(_icons_path_, 'tool_ticket.png')
_tool_update_ = os.path.join(_icons_path_, 'tool_update.png')
_tool_validate_ = os.path.join(_icons_path_, 'tool_validate.png')
_tool_comment_ = os.path.join(_icons_path_, 'tool_comment.png')
_random_icon_ = os.path.join(_icons_path_, 'random.svg')
_bulb_icon_ = os.path.join(_icons_path_, 'bulb.svg')
_info_icon_ = os.path.join(_icons_path_, 'info.svg')
_chip_icon_ = os.path.join(_icons_path_, 'chip_icon.svg')
_python_icon_ = os.path.join(_icons_path_, 'python.svg')
_console_icon_ = os.path.join(_icons_path_, 'console.svg')
_console_warning_icon_ = os.path.join(_icons_path_, 'console_warning.svg')
_console_error_icon_ = os.path.join(_icons_path_, 'console_error.svg')
_console_info_icon_ = os.path.join(_icons_path_, 'console_info.svg')
_tasks_icon_ = os.path.join(_icons_path_, 'tasks.svg')
_tasks_process_icon_ = os.path.join(_icons_path_, 'tasks_process.svg')
_tasks_done_icon_ = os.path.join(_icons_path_, 'tasks_done.svg')
_running_softwares_icon_ = os.path.join(_icons_path_, 'running_softwares.svg')
_wall_icon_ = os.path.join(_icons_path_, 'wall.svg')
_wall_notification_icon_ = os.path.join(_icons_path_, 'wall_notification.svg')
_wizard_icon_small_ = os.path.join(_icons_path_, 'wizard_icon_small.png')
_init_work_env_info_image_ = os.path.join(_icons_path_, 'init_work_env_info.png')
_select_stage_info_image_ = os.path.join(_icons_path_, 'select_stage_info.png')
_merge_info_image_ = os.path.join(_icons_path_, 'info_merge.png')
_chill_info_image_ = os.path.join(_icons_path_, 'info_chill.png')
_empty_info_image_ = os.path.join(_icons_path_, 'info_empty.png')
_tickets_info_image_ = os.path.join(_icons_path_, 'info_tickets.png')
_references_info_image_ = os.path.join(_icons_path_, 'info_references.png')
_lost_info_image_ = os.path.join(_icons_path_, 'info_lost.png')
_alone_info_ = os.path.join(_icons_path_, 'info_alone.png')
_nothing_info_ = os.path.join(_icons_path_, 'info_nothing.svg')
_no_connection_info_ = os.path.join(_icons_path_, 'info_no_connection.svg')
_handshake_icon_ = os.path.join(_icons_path_, 'handshake.png')
_messages_icon_ = os.path.join(_icons_path_, 'messages.svg')
_quit_decoration_ = os.path.join(_icons_path_, 'quit_decoration.svg')
_resize_decoration_ = os.path.join(_icons_path_, 'resize_decoration.svg')
_minimize_decoration_ = os.path.join(_icons_path_, 'minimize_decoration.svg')
_manual_export_ = os.path.join(_icons_path_, 'manual_export.svg')
_gold_icon_ = os.path.join(_icons_path_, 'gold.svg')
_silver_icon_ = os.path.join(_icons_path_, 'silver.svg')
_bronze_icon_ = os.path.join(_icons_path_, 'bronze.svg')
_ranking_icon_ = os.path.join(_icons_path_, 'ranking_icon.svg')
_kill_task_icon_ = os.path.join(_icons_path_, 'kill_task.svg')
_refresh_icon_ = os.path.join(_icons_path_, 'refresh_icon.svg')
_team_connection_on_ = os.path.join(_icons_path_, 'team_connection_on.svg')
_team_connection_off_ = os.path.join(_icons_path_, 'team_connection_off.svg')
_settings_icon_ = os.path.join(_icons_path_, 'settings.svg')
_user_icon_ = os.path.join(_icons_path_, 'user_icon.svg')
_save_icon_ = os.path.join(_icons_path_, 'save.svg')
_loading_image_ = os.path.join(_icons_path_, 'loading_image.png')
_state_todo_ = os.path.join(_icons_path_, 'state_todo.svg')
_state_wip_ = os.path.join(_icons_path_, 'state_wip.svg')
_state_done_ = os.path.join(_icons_path_, 'state_done.svg')
_state_error_ = os.path.join(_icons_path_, 'state_error.svg')
_estimated_time_icon_ = os.path.join(_icons_path_, 'estimated_time.svg')
_work_time_icon_ = os.path.join(_icons_path_, 'work_time.svg')
_password_visibility_on_ = os.path.join(_icons_path_, 'password_visibility_on.svg')
_password_visibility_off_ = os.path.join(_icons_path_, 'password_visibility_off.svg')
_create_project_image_ = os.path.join(_icons_path_, 'create_project.svg')
_project_manager_ = os.path.join(_icons_path_, 'project_manager.svg')
_create_icon_ =  os.path.join(_icons_path_, 'create.svg')
_documentation_icon_ =  os.path.join(_icons_path_, 'documentation.svg')
_license_icon_ =  os.path.join(_icons_path_, 'license.svg')

_references_icon_ = os.path.join(_icons_path_, 'reference_icon.svg')
_work_icon_ = os.path.join(_icons_path_, 'work_icon.svg')
_exports_icon_ = os.path.join(_icons_path_, 'export_icon.svg')
_tickets_icon_ = os.path.join(_icons_path_, 'tickets_icon.svg')


# Lock icons
_lock_icons_ = dict()
_lock_icons_[1] = os.path.join(_icons_path_, 'locked.svg')
_lock_icons_[0] = os.path.join(_icons_path_, 'unlocked.svg')

# Domains icons
_assets_icon_small_ = os.path.join(_icons_path_, 'assets_small.png')
_library_icon_small_ = os.path.join(_icons_path_, 'library_small.png')
_sequences_icon_small_ = os.path.join(_icons_path_, 'sequences_small.png')

# Stages icons
_modeling_icon_small_ = os.path.join(_icons_path_, 'modeling_small.png')
_rigging_icon_small_ = os.path.join(_icons_path_, 'rigging_small.png')
_grooming_icon_small_ = os.path.join(_icons_path_, 'grooming_small.png')
_texturing_icon_small_ = os.path.join(_icons_path_, 'texturing_small.png')
_shading_icon_small_ = os.path.join(_icons_path_, 'shading_small.png')

_layout_icon_small_ = os.path.join(_icons_path_, 'layout_small.png')
_animation_icon_small_ = os.path.join(_icons_path_, 'animation_small.png')
_cfx_icon_small_ = os.path.join(_icons_path_, 'cfx_small.png')
_fx_icon_small_ = os.path.join(_icons_path_, 'fx_small.png')
_lighting_icon_small_ = os.path.join(_icons_path_, 'lighting_small.png')
_compositing_icon_small_ = os.path.join(_icons_path_, 'compositing_small.png')
_camera_icon_small_ = os.path.join(_icons_path_, 'camera_small.png')

_stage_icons_dic_ = dict()
_stage_icons_dic_['modeling'] = _modeling_icon_small_
_stage_icons_dic_['rigging'] = _rigging_icon_small_
_stage_icons_dic_['grooming'] = _grooming_icon_small_
_stage_icons_dic_['texturing'] = _texturing_icon_small_
_stage_icons_dic_['shading'] = _shading_icon_small_
_stage_icons_dic_['layout'] = _layout_icon_small_
_stage_icons_dic_['animation'] = _animation_icon_small_
_stage_icons_dic_['cfx'] = _cfx_icon_small_
_stage_icons_dic_['fx'] = _fx_icon_small_
_stage_icons_dic_['lighting'] = _lighting_icon_small_
_stage_icons_dic_['compositing'] = _compositing_icon_small_
_stage_icons_dic_['camera'] = _camera_icon_small_

# Softwares icons
_sofwares_icons_dic_ = dict()
_sofwares_icons_dic_[_maya_] = os.path.join(_icons_path_, 'maya.svg')
_sofwares_icons_dic_[_guerilla_render_] = os.path.join(_icons_path_, 'guerilla_render.svg')
_sofwares_icons_dic_[_substance_painter_] = os.path.join(_icons_path_, 'substance_painter.svg')
_sofwares_icons_dic_[_substance_designer_] = os.path.join(_icons_path_, 'substance_designer.svg')
_sofwares_icons_dic_[_nuke_] = os.path.join(_icons_path_, 'nuke.svg')
_sofwares_icons_dic_[_houdini_] = os.path.join(_icons_path_, 'houdini.svg')
_sofwares_icons_dic_[_blender_] = os.path.join(_icons_path_, 'blender.svg')