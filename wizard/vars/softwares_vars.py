# coding: utf-8

# Available softwares
_maya_ = 'maya'
_guerilla_render_ = 'guerilla_render'
_substance_painter_ = 'substance_painter'
_substance_designer_ = 'substance_designer'
_nuke_ = 'nuke'
_houdini_ = 'houdini'
_blender_ = 'blender'

_softwares_list_ = [_maya_,
					_guerilla_render_,
					_substance_painter_,
					_substance_designer_,
					_nuke_,
					_blender_,
					_houdini_]

# Extensions
_softwares_extensions_dic_ = dict()
_softwares_extensions_dic_[_maya_] = 'ma'
_softwares_extensions_dic_[_guerilla_render_] = 'gproject'
_softwares_extensions_dic_[_substance_painter_] = 'spp'
_softwares_extensions_dic_[_substance_designer_] = 'sbs'
_softwares_extensions_dic_[_nuke_] = 'nk'
_softwares_extensions_dic_[_houdini_] = 'hip'
_softwares_extensions_dic_[_blender_] = 'blend'

# Launch commands
_executable_key_ = '[executable]'
_file_key_ = '[file]'
_script_key_ = '[startup_script]'
_reference_key_ = '[reference]'

_softwares_file_command_ = dict()
_softwares_file_command_[_maya_] = '"{}" -file "{}" -script "{}"'.format(_executable_key_, _file_key_, _script_key_)
_softwares_file_command_[_guerilla_render_] = '''"{}" "{}" --pycmd "execfile('{}')"'''.format(_executable_key_, _file_key_, _script_key_)
_softwares_file_command_[_substance_painter_] = '"{}" --mesh "{}" --split-by-udim "{}"'.format(_executable_key_, _reference_key_, _file_key_)
_softwares_file_command_[_substance_designer_] = '"{}" "{}"'.format(_executable_key_, _file_key_)
_softwares_file_command_[_nuke_] = '"{}" --nukex "{}"'.format(_executable_key_, _file_key_)
_softwares_file_command_[_houdini_] = '"{}" "{}" waitforui "{}" '.format(_executable_key_, _file_key_, _script_key_)
_softwares_file_command_[_blender_] = '"{}" "{}" --python "{}"'.format(_executable_key_, _file_key_, _script_key_)

_softwares_no_file_command_ = dict()
_softwares_no_file_command_[_maya_] = '"{}" -script "{}"'.format(_executable_key_, _script_key_)
_softwares_no_file_command_[_guerilla_render_] = '''"{}" --pycmd "execfile('{}')"'''.format(_executable_key_, _script_key_)
_softwares_no_file_command_[_substance_painter_] = '"{}" --mesh "{}" --split-by-udim'.format(_executable_key_, _reference_key_)
_softwares_no_file_command_[_substance_designer_] = '"{}"'.format(_executable_key_)
_softwares_no_file_command_[_nuke_] = '"{}" --nukex'.format(_executable_key_)
_softwares_no_file_command_[_houdini_] = '"{}" waitforui "{}" '.format(_executable_key_, _script_key_)
_softwares_no_file_command_[_blender_] = '"{}" --python "{}"'.format(_executable_key_, _script_key_)
