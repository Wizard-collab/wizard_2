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
import subprocess
import shlex
import json
import traceback
import logging

# Wizard modules
from wizard.core import launch
from wizard.core import assets
from wizard.core import project
from wizard.core import environment
from wizard.core import path_utils
from wizard.core import socket_utils
from wizard.vars import softwares_vars

# Wizard gui modules
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

def batch_export(version_id, settings_dic=None):
    work_version_row = project.get_version_data(version_id)
    if work_version_row:
        file_path = work_version_row['file_path']
        work_env_id = work_version_row['work_env_id']
        software_id = project.get_work_env_data(work_env_id, 'software_id')
        software_row = project.get_software_data(software_id)
        command = build_command(file_path, software_row, version_id)
        env = launch.build_env(work_env_id, software_row, version_id, mode='batch')
        env = add_settings_dic_to_env(env, settings_dic)
        if command :
            process = subprocess.Popen(args = shlex.split(command), env=env, cwd=path_utils.abspath('softwares'))
            logger.info(f"{software_row['name']} launched")
            process.wait()
            logger.info(f"{software_row['name']} closed")

def add_settings_dic_to_env(env, settings_dic):
    env['wizard_json_settings'] = json.dumps(settings_dic)
    return env

def build_command(file_path, software_row, version_id):
    software_batch_path = software_row['batch_path']
    if software_batch_path != '':
        if path_utils.isfile(file_path):
            raw_command = software_row['batch_file_command']
        else:
            raw_command = software_row['batch_no_file_command']
            logger.info("File not existing, launching software with empty scene")

        raw_command = raw_command.replace(softwares_vars._executable_key_, software_batch_path)
        raw_command = raw_command.replace(softwares_vars._file_key_, file_path)

        if software_row['name'] in softwares_vars._batch_scripts_dic_.keys():
            raw_command = raw_command.replace(softwares_vars._script_key_,
                                softwares_vars._batch_scripts_dic_[software_row['name']])
        return raw_command
    else:
        logger.warning(f"{software_row['name']} batch path not defined")
        return None