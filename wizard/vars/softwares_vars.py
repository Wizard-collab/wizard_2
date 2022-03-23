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
_extensions_dic_ = dict()
_extensions_dic_[_maya_] = 'ma'
_extensions_dic_[_guerilla_render_] = 'gproject'
_extensions_dic_[_substance_painter_] = 'spp'
_extensions_dic_[_substance_designer_] = 'sbs'
_extensions_dic_[_nuke_] = 'nk'
_extensions_dic_[_houdini_] = 'hip'
_extensions_dic_[_blender_] = 'blend'

# Launch commands
_executable_key_ = '[executable]'
_file_key_ = '[file]'
_script_key_ = '[startup_script]'
_reference_key_ = '[reference]'

_file_command_ = dict()
_file_command_[_maya_] = '"{}" -file "{}" -script "{}"'.format(_executable_key_, _file_key_, _script_key_)
_file_command_[_guerilla_render_] = '''"{}" "{}" --pycmd "execfile('{}')"'''.format(_executable_key_, _file_key_, _script_key_)
_file_command_[_substance_painter_] = '"{}" --mesh {} --split-by-udim "{}"'.format(_executable_key_, _reference_key_, _file_key_)
_file_command_[_substance_designer_] = '"{}" "{}"'.format(_executable_key_, _file_key_)
_file_command_[_nuke_] = '"{}" --nukex "{}"'.format(_executable_key_, _file_key_)
_file_command_[_houdini_] = '"{}" "{}" waitforui "{}" '.format(_executable_key_, _file_key_, _script_key_)
_file_command_[_blender_] = '"{}" "{}" --python "{}"'.format(_executable_key_, _file_key_, _script_key_)

_no_file_command_ = dict()
_no_file_command_[_maya_] = '"{}" -script "{}"'.format(_executable_key_, _script_key_)
_no_file_command_[_guerilla_render_] = '''"{}" --pycmd "execfile('{}')"'''.format(_executable_key_, _script_key_)
_no_file_command_[_substance_painter_] = '"{}" --mesh {} --split-by-udim'.format(_executable_key_, _reference_key_)
_no_file_command_[_substance_designer_] = '"{}"'.format(_executable_key_)
_no_file_command_[_nuke_] = '"{}" --nukex'.format(_executable_key_)
_no_file_command_[_houdini_] = '"{}" waitforui "{}" '.format(_executable_key_, _script_key_)
_no_file_command_[_blender_] = '"{}" --python "{}"'.format(_executable_key_, _script_key_)

_batch_file_command_ = dict()
_batch_file_command_[_maya_] = '"{}" -file "{}" -script "{}"'.format(_executable_key_, _file_key_, _script_key_)
_batch_file_command_[_guerilla_render_] = '''"{}" "{}" --nogui --pycmd "execfile('{}')"'''.format(_executable_key_, _file_key_, _script_key_)
_batch_file_command_[_substance_painter_] = ''
_batch_file_command_[_substance_designer_] = ''
_batch_file_command_[_nuke_] = ''
_batch_file_command_[_houdini_] = ''
_batch_file_command_[_blender_] = '"{}" "{}" -b --python "{}"'.format(_executable_key_, _file_key_, _script_key_)

_batch_no_file_command_ = dict()
_batch_no_file_command_[_maya_] = '"{}" -script "{}"'.format(_executable_key_, _script_key_)
_batch_no_file_command_[_guerilla_render_] = '''"{}" --nogui --pycmd "execfile('{}')"'''.format(_executable_key_, _script_key_)
_batch_no_file_command_[_substance_painter_] = ''
_batch_no_file_command_[_substance_designer_] = ''
_batch_no_file_command_[_nuke_] = ''
_batch_no_file_command_[_houdini_] = ''
_batch_no_file_command_[_blender_] = '"{}" -b --python "{}"'.format(_executable_key_, _script_key_)

# Environments
_script_env_dic_=dict()
_script_env_dic_[_maya_]='PYTHONPATH'
_script_env_dic_[_guerilla_render_]='PYTHONPATH'
_script_env_dic_[_substance_painter_]='SUBSTANCE_PAINTER_PLUGINS_PATH'
_script_env_dic_[_substance_designer_]='SBS_DESIGNER_PYTHON_PATH'
_script_env_dic_[_nuke_]='NUKE_PATH'
_script_env_dic_[_houdini_]='PYTHONPATH'
_script_env_dic_[_blender_]='PYTHONPATH'

# Plugins path
_main_script_path_ = path_utils.clean_path(path_utils.abspath('softwares'))
_plugins_path_ = dict()
_plugins_path_[_maya_] = path_utils.clean_path(path_utils.abspath(path_utils.join('softwares', 'maya_wizard')))
_plugins_path_[_guerilla_render_] = path_utils.clean_path(path_utils.abspath(path_utils.join('softwares', 'guerilla_render_wizard')))
_plugins_path_[_substance_painter_] = path_utils.clean_path(path_utils.abspath(path_utils.join('softwares', 'substance_painter_wizard')))
_plugins_path_[_substance_designer_] = path_utils.clean_path(path_utils.abspath(path_utils.join('softwares', 'substance_designer_wizard')))
_plugins_path_[_nuke_] = path_utils.clean_path(path_utils.abspath(path_utils.join('softwares', 'nuke_wizard')))
_plugins_path_[_houdini_] = path_utils.clean_path(path_utils.abspath(path_utils.join('softwares', 'houdini_wizard')))
_plugins_path_[_blender_]  = path_utils.clean_path(path_utils.abspath(path_utils.join('softwares', 'blender_wizard')))

# Scripts files
_scripts_dic_ = dict()
_scripts_dic_[_maya_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_maya_], 'startup.mel'))).replace('\\', '/')
_scripts_dic_[_guerilla_render_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_guerilla_render_], 'startup.py'))).replace('\\', '/')
_scripts_dic_[_blender_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_blender_], 'startup.py'))).replace('\\', '/')
_scripts_dic_[_houdini_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_houdini_], 'startup.py'))).replace('\\', '/')

_batch_scripts_dic_ = dict()
_batch_scripts_dic_[_maya_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_maya_], 'batch_startup.mel'))).replace('\\', '/')
_batch_scripts_dic_[_guerilla_render_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_guerilla_render_], 'batch_startup.py'))).replace('\\', '/')
_batch_scripts_dic_[_blender_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_blender_], 'batch_startup.py'))).replace('\\', '/')
_batch_scripts_dic_[_houdini_] = path_utils.clean_path(path_utils.abspath(path_utils.join(_plugins_path_[_houdini_], 'batch_startup.py'))).replace('\\', '/')

_hooks_files_ = dict()
_hooks_files_[_maya_] = 'maya_hook.py'
_hooks_files_[_blender_] = 'blender_hook.py'
_hooks_files_[_substance_painter_] = 'substance_painter_hook.py'
_hooks_files_[_guerilla_render_] = 'guerilla_render_hook.py'