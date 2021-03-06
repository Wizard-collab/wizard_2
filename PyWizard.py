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

# PyWizard is the wizard application without GUI
# Use PyWizard to execute batch commands like
# large amount of instances creation or archiving

# Python modules
import sys
import os
import traceback
import code
from PyQt5 import QtWidgets
import logging

# Append current dir to sys.path
sys.path.append(os.path.abspath(''))

# Wizard gui modules
from wizard.gui import gui_utils
from wizard.gui import gui_server

# Wizard modules
from wizard.core import application
from wizard.core import user
from wizard.core import project
from wizard.core import repository
from wizard.core import tools
from wizard.core import create_project
from wizard.core import communicate
from wizard.core import environment
from wizard.core import launch
from wizard.core import launch_batch
from wizard.core import db_core
from wizard.core import custom_logger
custom_logger.get_root_logger()
logger = logging.getLogger(__name__)

application.log_app_infos()
print('PyWizard')

app = gui_utils.get_app()

while not user.user().get_psql_dns():
    psql_host = tools.flushed_input("PostgreSQL host : ")
    psql_port = tools.flushed_input("PostgreSQL port : ")
    psql_user = tools.flushed_input("PostgreSQL user : ")
    psql_password = tools.flushed_input("PostgreSQL password : ")
    user.user().set_psql_dns(
                            psql_host,
                            psql_port,
                            psql_user,
                            psql_password
                            )

db_server = db_core.db_server()
db_server.start()

if not user.user().get_repository():
    input_repository = tools.flushed_input("repository : ")
    user.user().set_repository(input_repository)

if not repository.is_repository_database():
    while not repository.is_repository_database():
        init_repository = tools.flushed_input("Warning, repository database doesn't exists, init database (y/n) ? : ")
        if init_repository == 'y':
            admin_password = tools.flushed_input('Administator password : ')
            admin_email = tools.flushed_input('Administator email : ')
            repository.create_repository_database()
            db_server.repository='repository'
            repository.init_repository(admin_password, admin_email)

db_server.repository=environment.get_repository()
repository.add_ip_user()

while not user.get_user():
    do_create_user = tools.flushed_input('Create user (y/n) ? : ')
    if do_create_user == 'y':
        user_name = tools.flushed_input('User name : ')
        password = tools.flushed_input('Password : ')
        email = tools.flushed_input('Email : ')
        profile_picture = tools.flushed_input('Profile picture ( without any "\\" ) ( Optional ) : ')
        administrator_pass = tools.flushed_input('Administrator pass ( Optional ) : ')
        repository.create_user(user_name,
                                password,
                                email,
                                administrator_pass,
                                profile_picture)
    else:
        user_name = tools.flushed_input('User name : ')
        password = tools.flushed_input('Password : ')
        user.log_user(user_name, password)

while not user.get_project():
    do_create_project = tools.flushed_input('Create project (y/n) ? : ')
    if do_create_project == 'y':
        project_name = tools.flushed_input('Project name : ')
        project_path = tools.flushed_input('Project path : ')
        project_password = tools.flushed_input('Project password : ')
        create_project.create_project(project_name, project_path, project_password)
    else:
        project_name = tools.flushed_input('Project name : ')
        project_password = tools.flushed_input('Project password : ')
        user.log_project(project_name, project_password)

db_server.project_name = environment.get_project_name()

communicate_server = communicate.communicate_server()
communicate_server.start()

softwares_server = launch.softwares_server()
softwares_server.start()

console = code.InteractiveConsole()
console.interact(banner=None, exitmsg=None)
    
db_server.stop()
softwares_server.stop()
communicate_server.stop()
