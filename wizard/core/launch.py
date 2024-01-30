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

# The main wizard software launching module
# This module permits to launch a work version ( id )
# It build the command and environment for the Popen
# call

# If no file is found for the given version id
# it launches the software without a file but 
# with the correct environment in order to save
# a version later within the software

# Python modules
import os
import subprocess
import shlex
import json
import traceback
import time
from threading import Thread
import logging

# Wizard modules
from wizard.core import user
from wizard.core import assets
from wizard.core import project
from wizard.core import environment
from wizard.core import socket_utils
from wizard.core import path_utils
from wizard.vars import softwares_vars

# Wizard gui modules
from wizard.gui import gui_server

logger = logging.getLogger(__name__)

def launch_work_version(version_id):
    signal_dic = dict()
    signal_dic['function'] = 'launch'
    signal_dic['version_id'] = version_id
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=0.5)

def kill(work_env_id):
    signal_dic = dict()
    signal_dic['function'] = 'kill'
    signal_dic['work_env_id'] = work_env_id
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=100)

def kill_all():
    signal_dic = dict()
    signal_dic['function'] = 'kill_all'
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=100)

def died(work_env_id):
    signal_dic = dict()
    signal_dic['function'] = 'died'
    signal_dic['work_env_id'] = work_env_id
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=0.5)

def get():
    signal_dic = dict()
    signal_dic['function'] = 'get'
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=0.5)

def core_kill_software_thread(software_thread):
    return software_thread.kill()

def core_launch_version(version_id):
    work_version_row = project.get_version_data(version_id)
    if not work_version_row:
        return None, None
    file_path = work_version_row['file_path']
    work_env_id = work_version_row['work_env_id']
    user.user().add_recent_scene((work_env_id, time.time()))
    if project.get_lock(work_env_id):
        return None, None
    project.set_work_env_lock(work_env_id)
    software_id = project.get_work_env_data(work_env_id, 'software_id')
    software_row = project.get_software_data(software_id)
    command = build_command(file_path, software_row, version_id)
    env = build_env(work_env_id, software_row, version_id)
    if not command :
        return None, None
    thread = software_thread(command,
                                env,
                                software_row['name'],
                                work_env_id)
    thread.start()
    logger.info(f"{software_row['name']} launched")
    return thread, work_env_id

def build_command(file_path, software_row, version_id):
    software_path = software_row['path']
    if not os.path.isfile(software_path):
        logger.warning(f"{software_row['name']} not found ( {software_path} does not exists )")
        return
    if software_path == '':
        logger.warning(f"{software_row['name']} path not defined")
        return
    if path_utils.isfile(file_path):
        raw_command = software_row['file_command']
    else:
        raw_command = software_row['no_file_command']
        logger.info("File not existing, launching software with empty scene")

    raw_command = raw_command.replace(softwares_vars._executable_key_, software_path)
    raw_command = raw_command.replace(softwares_vars._file_key_, file_path)

    # Substance Painter specific launch
    if software_row['name'] == softwares_vars._substance_painter_:
        work_env_id = project.get_version_data(version_id, 'work_env_id')
        references_dic = assets.get_references_files(work_env_id) 
        if 'modeling' in references_dic.keys():
            reference_file = references_dic['modeling'][0]['files'][0]
            raw_command = raw_command.replace(softwares_vars._reference_key_,
                                                reference_file.replace('\\', '/'))
        else:
            logger.warning('Please create ONE modeling reference to launch Substance Painter')

    if software_row['name'] in softwares_vars._scripts_dic_.keys():
        raw_command = raw_command.replace(softwares_vars._script_key_,
                            softwares_vars._scripts_dic_[software_row['name']])
    return raw_command

def build_env(work_env_id, software_row, version_id, mode='gui'):
    # Building the default software environment for wizard workflow
    env = os.environ.copy()
    env['wizard_launch_mode'] = mode
    env['wizard_work_env_id'] = str(work_env_id)
    env['wizard_version_id'] = str(version_id)

    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    stage_row = project.get_stage_data(stage_id)
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    env['wizard_stage_name'] = str(stage_row['name'])
    env['wizard_asset_name'] = str(asset_row['name'])
    env['wizard_category_name'] = str(category_row['name'])

    env[softwares_vars._script_env_dic_[software_row['name']]] = softwares_vars._main_script_path_
    env[softwares_vars._script_env_dic_[software_row['name']]] += os.pathsep + project.get_hooks_folder()

    # Substance Painter specific env
    if software_row['name'] == softwares_vars._substance_painter_:
        env[softwares_vars._script_env_dic_[software_row['name']]] += os.pathsep + softwares_vars._plugins_path_[software_row['name']]

    # Houdini specific env
    if software_row['name'] == softwares_vars._houdini_:
        env['HOUDINI_MENU_PATH'] = f"{softwares_vars._plugins_path_[software_row['name']]};&"

    # Nuke specific env
    if software_row['name'] == softwares_vars._nuke_:
        if 'NUKE_PATH' in env.keys():
            env['NUKE_PATH'] += os.pathsep + softwares_vars._plugins_path_[software_row['name']]

    # Getting the project software additionnal environment
    additionnal_script_paths = []
    if software_row['additionnal_scripts']:
        additionnal_script_paths = json.loads(software_row['additionnal_scripts'])
    additionnal_env = dict()
    if software_row['additionnal_env']:
        additionnal_env = json.loads(software_row['additionnal_env'])

    # Merging the project software additionnal environment
    # to the main env variable
    if type(additionnal_script_paths) == str:
        additionnal_script_paths = additionnal_script_paths.split('\n')
    for script_path in additionnal_script_paths:
        env[softwares_vars._script_env_dic_[software_row['name']]] += os.pathsep+script_path

    for key in additionnal_env.keys():
        if key in env.keys():
            env[key] += os.pathsep+additionnal_env[key]
        else:
            env[key] = additionnal_env[key]

    if 'PYTHONPATH' in env.keys():
        python_path_list = env['PYTHONPATH'].split(';')
        for path in python_path_list:
            if 'Wizard/_internal' in path:
                python_path_list.remove(path)
        env['PYTHONPATH'] = (';').join(python_path_list)

    if software_row['name'] == 'blender':
        import PyQt5
        pyqt5_path = path_utils.dirname(path_utils.dirname(PyQt5.__file__))
        logger.info(pyqt5_path)
        env[softwares_vars._script_env_dic_[software_row['name']]] += os.pathsep+pyqt5_path

    # Clean QT from env
    if 'QT_PLUGIN_PATH' in env.keys():
        del env['QT_PLUGIN_PATH']
    if 'QML2_IMPORT_PATH' in env.keys():
        del env['QML2_IMPORT_PATH']
    if 'QT_AUTO_SCREEN_SCALE_FACTOR' in env.keys():
        del env['QT_AUTO_SCREEN_SCALE_FACTOR']

    return env

class software_thread(Thread):
    ''' A thread that runs until the given software process is active
    When the software process is exited, the thread is deleted
    '''
    def __init__(self, command, env, software, work_env_id):
        super(software_thread, self).__init__()
        self.command = command
        self.env = env
        self.software = software
        self.work_env_id = work_env_id
        self.killed = False
        self.start_time = time.perf_counter()
 
    def run(self):
        self.process = subprocess.Popen(args = shlex.split(self.command), env=self.env, cwd=path_utils.abspath('softwares'))
        self.process.wait()
        died(self.work_env_id)
        if not self.killed:
            self.set_infos()
            gui_server.refresh_ui()

    def set_infos(self):
        work_time = time.perf_counter()-self.start_time
        project.set_work_env_lock(self.work_env_id, 0)
        assets.add_work_time(self.work_env_id, work_time)
        user.user().add_recent_scene((self.work_env_id, time.time()))
        logger.info(f"{self.software} closed")

    def kill(self):
        self.process.kill()
        self.process.wait()
        self.killed = True
        self.set_infos()
        logger.info(f"{self.software} killed")
        return 1

class softwares_server(Thread):
    ''' A "server" thread that manage softwares processes
    It permits to launch and kill software subprocesses
    '''
    def __init__(self):
        super(softwares_server, self).__init__()
        self.port = socket_utils.get_port('localhost')
        environment.set_softwares_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(('localhost',
                                                                    self.port))
        self.running = True
        self.software_threads_dic = dict()

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] != self.server_address:
                    continue
                signal_as_str = socket_utils.recvall(conn)
                if not signal_as_str:
                    continue
                self.analyse_signal(signal_as_str.decode('utf8'), conn)
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))

    def stop(self):
        self.server.close()
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        # The signal_as_str is already decoded ( from utf8 )
        # The incoming signal needs to be a json string
        returned = 0
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'launch':
            returned = self.launch(signal_dic['version_id'])
        if signal_dic['function'] == 'kill':
            returned = self.kill(signal_dic['work_env_id'])
        if signal_dic['function'] == 'kill_all':
            returned = self.kill_all()
        if signal_dic['function'] == 'get':
            returned = list(self.software_threads_dic.keys())
        if signal_dic['function'] == 'died':
            returned = self.remove(signal_dic['work_env_id'])

        socket_utils.send_signal_with_conn(conn, returned)

    def launch(self, version_id):
        work_env_id = project.get_version_data(version_id, 'work_env_id')
        if not work_env_id:
            return
        if work_env_id in self.software_threads_dic.keys():
            logger.warning(f"You are already running a work instance of this asset")
            return
        software_thread, work_env_id = core_launch_version(version_id)
        if software_thread is not None:
            self.software_threads_dic[work_env_id] = software_thread
        return work_env_id

    def kill_all(self):
        software_threads_ids = list(self.software_threads_dic.keys())
        if software_threads_ids is None:
            return
        for work_env_id in software_threads_ids:
            self.kill(work_env_id)
        return 1

    def kill(self, work_env_id):
        if work_env_id not in self.software_threads_dic.keys():
            logger.warning("Work environment not running or not found")
            return
        software_thread = self.software_threads_dic[work_env_id]
        self.remove(work_env_id)
        return core_kill_software_thread(software_thread)

    def remove(self, work_env_id):
        if work_env_id in self.software_threads_dic.keys():
            del self.software_threads_dic[work_env_id]
        return 1
