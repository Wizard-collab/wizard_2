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

# Softwares
_maya_ = 'maya'
_guerilla_render_ = 'guerilla_render'
_substance_painter_ = 'substance_painter'
_substance_designer_ = 'substance_designer'
_nuke_ = 'nuke'
_houdini_ = 'houdini'
_blender_ = 'blender'

# Domain vars
_assets_ = 'assets'
_library_ = 'library'
_sequences_ = 'sequences'
_domains_list_ = [_assets_, _library_, _sequences_]
_domains_list_no_lib_ = [_assets_, _sequences_]

_assets_id_ = 1
_library_id_ = 2
_sequences_id_ = 3

# Asset categories vars
_characters_ = 'characters'
_props_ = 'props'
_sets_ = 'sets'
_set_dress_ = 'set_dress'
_assets_categories_list_ = [_characters_,
							_props_,
							_sets_,
							_set_dress_]

# Asset stages vars
_modeling_ = 'modeling'
_rigging_ = 'rigging'
_grooming_ = 'grooming'
_texturing_ = 'texturing'
_shading_ = 'shading'

_custom_stage_ = 'custom'
_camera_rig_ = 'camrig'

_layout_ = 'layout'
_animation_ = 'animation'
_cfx_ = 'cfx'
_fx_ = 'fx'
_camera_ = 'camera'
_lighting_ = 'lighting'
_compositing_ = 'compositing'

_all_stages_ = [_modeling_,
				_rigging_,
				_grooming_,
				_texturing_,
				_shading_,
				_custom_stage_,
				_camera_rig_,
				_layout_, 
				_animation_,
				_cfx_,
				_fx_,
				_camera_,
				_lighting_,
				_compositing_,
				]

# Stage rules
_assets_stages_list_ = [_modeling_,
							_rigging_,
							_grooming_,
							_texturing_,
							_shading_]

_sequences_stages_list_ = [_layout_, 
								_animation_,
								_cfx_,
								_fx_,
								_camera_,
								_lighting_,
								_compositing_,
								]

_library_stages_list_ = _assets_stages_list_ + _sequences_stages_list_ + [_custom_stage_, _camera_rig_]

_camera_export_stages_ = [_animation_, _layout_]

_stages_list_ = dict()
_stages_list_[_assets_] = _assets_stages_list_
_stages_list_[_library_] = _library_stages_list_
_stages_list_[_sequences_] = _sequences_stages_list_

_stages_rules_dic_ = dict()
_stages_rules_dic_[_assets_] = _assets_stages_list_
_stages_rules_dic_[_sequences_] = _sequences_stages_list_
_stages_rules_dic_[_library_] = _library_stages_list_

_ext_dic_ = dict()
_ext_dic_[_modeling_] = dict()
_ext_dic_[_modeling_][_maya_] = ['abc', 'ma', 'obj', 'fbx']
_ext_dic_[_modeling_][_blender_] = ['abc', 'blend', 'fbx']
_ext_dic_[_modeling_][_houdini_] = ['abc', 'hip']
_ext_dic_[_rigging_] = dict()
_ext_dic_[_rigging_][_maya_] = ['ma']
_ext_dic_[_rigging_][_blender_] = ['blend']
_ext_dic_[_rigging_][_houdini_] = ['hip']
_ext_dic_[_grooming_] = dict()
_ext_dic_[_grooming_][_maya_] = ['ma']
_ext_dic_[_grooming_][_blender_] = ['blend']
_ext_dic_[_grooming_][_houdini_] = ['hip', 'abc']
_ext_dic_[_texturing_] = dict()
_ext_dic_[_texturing_][_maya_] = ['exr', 'png', 'tiff']
_ext_dic_[_texturing_][_blender_] = ['exr', 'png']
_ext_dic_[_texturing_][_substance_painter_] = ['exr', 'png']
_ext_dic_[_texturing_][_substance_designer_] = ['sbsar', 'exr', 'png']
_ext_dic_[_texturing_][_houdini_] = ['exr', 'png', 'tiff']
_ext_dic_[_shading_] = dict()
_ext_dic_[_shading_][_maya_] = ['ma']
_ext_dic_[_shading_][_blender_] = ['blend']
_ext_dic_[_shading_][_guerilla_render_] = ['gnode', 'gproject']
_ext_dic_[_shading_][_houdini_] = ['hip']
_ext_dic_[_layout_] = dict()
_ext_dic_[_layout_][_maya_] = ['abc', 'ma', 'fbx']
_ext_dic_[_layout_][_blender_] = ['abc', 'blend', 'fbx']
_ext_dic_[_layout_][_houdini_] = ['abc', 'hip']
_ext_dic_[_animation_] = dict()
_ext_dic_[_animation_][_maya_] = ['abc', 'ma']
_ext_dic_[_animation_][_blender_] = ['abc', 'blend']
_ext_dic_[_animation_][_houdini_] = ['abc', 'hip']
_ext_dic_[_cfx_] = dict()
_ext_dic_[_cfx_][_maya_] = ['abc', 'ma', 'fur']
_ext_dic_[_cfx_][_blender_] = ['abc', 'blend']
_ext_dic_[_cfx_][_houdini_] = ['abc', 'hip']
_ext_dic_[_fx_] = dict()
_ext_dic_[_fx_][_maya_] = ['abc', 'ma', 'vdb']
_ext_dic_[_fx_][_blender_] = ['abc', 'blend', 'vdb']
_ext_dic_[_fx_][_houdini_] = ['abc', 'hip', 'vdb']
_ext_dic_[_camera_] = dict()
_ext_dic_[_camera_][_maya_] = ['abc', 'ma']
_ext_dic_[_camera_][_blender_] = ['abc', 'blend']
_ext_dic_[_camera_][_houdini_] = ['abc', 'hip']
_ext_dic_[_lighting_] = dict()
_ext_dic_[_lighting_][_maya_] = ['exr']
_ext_dic_[_lighting_][_blender_] = ['exr']
_ext_dic_[_lighting_][_guerilla_render_] = ['exr']
_ext_dic_[_lighting_][_houdini_] = ['exr']
_ext_dic_[_compositing_] = dict()
_ext_dic_[_compositing_][_blender_] = ['exr']
_ext_dic_[_compositing_][_nuke_] = ['exr']
_ext_dic_[_custom_stage_] = dict()
_ext_dic_[_custom_stage_][_maya_] = ['ma', 'abc']
_ext_dic_[_custom_stage_][_blender_] = ['blend', 'abc']
_ext_dic_[_custom_stage_][_houdini_] = ['vdb', 'abc', 'hip']
_ext_dic_[_custom_stage_][_guerilla_render_] = ['gproject', 'gnode']
_ext_dic_[_custom_stage_][_substance_painter_] = ['sbsar']
_ext_dic_[_custom_stage_][_substance_designer_] = ['sbsar']
_ext_dic_[_custom_stage_][_nuke_] = ['nk']
_ext_dic_[_camera_rig_] = dict()
_ext_dic_[_camera_rig_][_maya_] = ['ma']
_ext_dic_[_camera_rig_][_blender_] = ['blend']
_ext_dic_[_camera_rig_][_houdini_] = ['hip']

# Stages softwares rules
_stage_softwares_rules_dic_ = dict()
_stage_softwares_rules_dic_[_modeling_] = [_maya_, _houdini_, _blender_]
_stage_softwares_rules_dic_[_rigging_] = [_maya_, _houdini_, _blender_]
_stage_softwares_rules_dic_[_grooming_] = [_maya_, _houdini_, _blender_, _guerilla_render_]
_stage_softwares_rules_dic_[_texturing_] = [_substance_painter_, _substance_designer_, _maya_, _houdini_, _blender_, _guerilla_render_]
_stage_softwares_rules_dic_[_shading_] = [_guerilla_render_, _maya_, _houdini_, _blender_]
_stage_softwares_rules_dic_[_layout_] = [_maya_, _houdini_, _blender_]
_stage_softwares_rules_dic_[_animation_] = [_maya_, _houdini_, _blender_]
_stage_softwares_rules_dic_[_cfx_] = [_houdini_, _maya_, _blender_]
_stage_softwares_rules_dic_[_fx_] = [_houdini_, _maya_, _blender_]
_stage_softwares_rules_dic_[_camera_] = [_maya_, _houdini_, _blender_]
_stage_softwares_rules_dic_[_lighting_] = [_guerilla_render_, _maya_, _houdini_, _blender_]
_stage_softwares_rules_dic_[_compositing_] = [_nuke_, _blender_]
_stage_softwares_rules_dic_[_custom_stage_] = [_maya_, _blender_, _houdini_, _guerilla_render_, _substance_painter_, _substance_designer_, _nuke_ ]
_stage_softwares_rules_dic_[_camera_rig_] = [_maya_, _blender_, _houdini_]

# Asset states
_asset_state_todo_ = 'todo'
_asset_state_wip_ = 'wip'
_asset_state_done_ = 'done'
_asset_state_error_ = 'error'
_asset_state_rtk_ = 'rtk'
_asset_state_wfa_ = 'wfa'
_asset_state_omt_ = 'omt'
_asset_states_list_ = [_asset_state_todo_,
						_asset_state_wip_,
						_asset_state_done_,
						_asset_state_error_,
						_asset_state_rtk_,
						_asset_state_wfa_,
						_asset_state_omt_]

# Asset urgence
_priority_normal_ = 'normal'
_priority_high_ = 'high'
_priority_urgent_ = 'urgent'
_priority_list_ = [_priority_normal_,
				_priority_high_,
				_priority_urgent_]
