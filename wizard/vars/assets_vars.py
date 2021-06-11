# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

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
_compositing_ = 'compositing'
_fx_ = 'fx'

# Stage rules
_assets_stage_rules_dic_ = dict()
_assets_stage_rules_dic_[_characters_] = [_modeling_,
										_rigging_,
										_grooming_,
										_texturing_,
										_shading_]
_assets_stage_rules_dic_[_props_] = [_modeling_,
									_rigging_,
									_grooming_,
									_texturing_,
									_shading_]
_assets_stage_rules_dic_[_sets_] = [_modeling_,
									_grooming_,
									_texturing_,
									_shading_]
_assets_stage_rules_dic_[_set_dress_] = [_modeling_,
										_grooming_,
										_texturing_,
										_shading_]

# Export rules
''' The _export_ext_dic_ dictionnary 
stores the software export extensions rules as
list depending on the software and the stage 
'''
_export_ext_dic_ = {}
_export_ext_dic_[_maya_] = {}
_export_ext_dic_[_blender_] = {}
_export_ext_dic_[_substance_painter_] = {}
_export_ext_dic_[_substance_designer_] = {}
_export_ext_dic_[_guerilla_render_] = {}
_export_ext_dic_[_nuke_] = {}
_export_ext_dic_[_houdini_] = {}
_export_ext_dic_[_maya_][_modeling_] = ['abc', 'ma']
_export_ext_dic_[_maya_][_rigging_] = ['ma']
_export_ext_dic_[_maya_][_grooming_] = ['ma']
_export_ext_dic_[_maya_][_shading_] = ['ma']
_export_ext_dic_[_blender_][_modeling_] = ['abc', 'blend']
_export_ext_dic_[_blender_][_rigging_] = ['blend']
_export_ext_dic_[_substance_painter_][_texturing_] = ['exr', 'png', 'tiff']
_export_ext_dic_[_substance_designer_][_texturing_] = ['sbsar']
_export_ext_dic_[_guerilla_render_][_shading_] = ['gnode']
_export_ext_dic_[_nuke_][_compositing_] = ['exr']
_export_ext_dic_[_houdini_][_fx_] = ['hip', 'vdb', 'abc']


# Default export dic
''' The _default_ext_dic_ dictionnary 
stores the default software export extensions as
strings depending on the software and the stage
'''
_default_ext_dic_ = {}
_default_ext_dic_[_maya_] = {}
_default_ext_dic_[_blender_] = {}
_default_ext_dic_[_substance_painter_] = {}
_default_ext_dic_[_substance_designer_] = {}
_default_ext_dic_[_guerilla_render_] = {}
_default_ext_dic_[_nuke_] = {}
_default_ext_dic_[_houdini_] = {}
_default_ext_dic_[_maya_][_modeling_] = 'abc'
_default_ext_dic_[_maya_][_rigging_] = 'ma'
_default_ext_dic_[_maya_][_grooming_] = 'ma'
_default_ext_dic_[_maya_][_shading_] = 'ma'
_default_ext_dic_[_blender_][_modeling_] = 'abc'
_default_ext_dic_[_blender_][_rigging_] = 'blend'
_default_ext_dic_[_substance_painter_][_texturing_] = 'exr'
_default_ext_dic_[_substance_designer_][_texturing_] = 'sbsar'
_default_ext_dic_[_guerilla_render_][_shading_] = 'gnode'
_default_ext_dic_[_nuke_][_compositing_] = 'exr'
_default_ext_dic_[_houdini_][_fx_] = 'abc'
