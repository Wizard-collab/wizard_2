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

# Main wizard module to create a project
# This module basically store the new project
# in the repository database, create the project database
# and create the intial instances :
# - assets
#    - characters
#    - props
#    - sets
#    - set_dress
# - library
# - sequences
# It intialize the defaults softwares in the 
# project database and initialize the project settings

# Python modules
import time
import datetime
import logging

# Wizard modules
from wizard.core import project
from wizard.core import user
from wizard.core import db_utils
from wizard.core import assets
from wizard.core import environment
from wizard.core import tools
from wizard.core import path_utils
from wizard.vars import assets_vars
from wizard.vars import project_vars
from wizard.vars import softwares_vars
logger = logging.getLogger(__name__)

# Python modules
import os

def get_default_deadline():
    deadline_string = datetime.datetime.fromtimestamp(time.time()+23328000).strftime('%d/%m/%Y')
    return deadline_string

def create_project(project_name,
                    project_path,
                    project_password,
                    frame_rate=24,
                    image_format=[1920,1080],
                    project_image=None,
                    deadline=get_default_deadline()):
    do_creation = 1
    if project_name == '':
        logger.warning("Please provide a project name")
        do_creation = 0
    if project_path == '':
        logger.warning("Please provide a project path")
        do_creation = 0
    if project_password == '':
        logger.warning("Please provide a password")
        do_creation = 0
    deadline_float = tools.get_time_float_from_string_date(deadline)
    if not deadline_float:
        do_creation = 0
    if not do_creation: 
        return
    old_project_name = environment.get_project_name()
    if not project.create_project(project_name, project_path, project_password, project_image):
        return
    db_utils.modify_db_name('project', project_name)
    init_project(project_name, project_path, project_password, frame_rate, image_format, deadline_float)
    if old_project_name is not None:
        user.log_project_without_cred(old_project_name)
    return 1


def init_project(project_name,
                    project_path,
                    project_password,
                    frame_rate=24,
                    image_format=[1920,1080],
                    deadline=time.time()+23328000):
    do_creation = 1
    if project_name == '':
        logger.warning("Please provide a project name")
        do_creation = 0
    if project_path == '':
        logger.warning("Please provide a project path")
        do_creation = 0
    if project_password == '':
        logger.warning("Please provide a password")
        do_creation = 0
    if not do_creation: 
        return
    project.create_settings_row(frame_rate, image_format, deadline)
    for domain in assets_vars._domains_list_:
        assets.create_domain(domain)
    assets_domain_id = 1
    for category in assets_vars._assets_categories_list_:
        assets.create_category(category, assets_domain_id)
    for software in softwares_vars._softwares_list_:
        software_id = project.add_software(software,
                        softwares_vars._extensions_dic_[software],
                        softwares_vars._file_command_[software],
                        softwares_vars._no_file_command_[software],
                        softwares_vars._batch_file_command_[software],
                        softwares_vars._batch_no_file_command_[software])
        for stage in assets_vars._ext_dic_.keys():
            if software in assets_vars._ext_dic_[stage].keys():
                extension = assets_vars._ext_dic_[stage][software][0]
                project.create_extension_row(stage, software_id, extension)

    tools.create_folder(project.get_shared_files_folder())
    tools.create_folder(project.get_scripts_folder())
    tools.create_folder(project.get_hooks_folder())
    tools.create_folder(project.get_plugins_folder())
    init_hooks()
    return 1

def init_hooks():
    hooks_dir = 'ressources/hooks'
    for file in os.listdir(hooks_dir):
        base = path_utils.join(hooks_dir, file)
        destination = path_utils.join(project.get_hooks_folder(), file) 
        path_utils.copyfile(base, destination)
