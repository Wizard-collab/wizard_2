# coding: utf-8

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
