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

# This module is used to handle third party softwares commands
# For example if you want to save a version within a
# Maya, the software plugin sends a socket signal
# here and waits for a return ( also socket signal )

# It roughly is a lan access to the wizard core functions

# Python modules
from threading import Thread
import traceback
import json
import logging

# Wizard gui modules
from wizard.gui import gui_server

# Wizard modules
from wizard.core import environment
from wizard.core import socket_utils
from wizard.core import assets
from wizard.core import user
from wizard.core import project
from wizard.core import video
from wizard.vars import user_vars
from wizard.vars import ressources

logger = logging.getLogger(__name__)


class communicate_server(Thread):
    def __init__(self):
        super(communicate_server, self).__init__()
        self.port = socket_utils.get_port('localhost')
        environment.set_communicate_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(
            ('localhost', self.port))
        self.running = True

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn)
                    if signal_as_str:
                        self.analyse_signal(signal_as_str.decode('utf8'), conn)
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.server.close()
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        # The signal_as_str is already decoded ( from utf8 )
        # The incoming signal needs to be a json string
        returned = None
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'add_version':
            returned = add_version(signal_dic['work_env_id'],
                                   signal_dic['comment'])
        elif signal_dic['function'] == 'get_file':
            returned = get_file(signal_dic['version_id'])
        elif signal_dic['function'] == 'request_export':
            returned = request_export(signal_dic['work_env_id'],
                                      signal_dic['export_name'])
        elif signal_dic['function'] == 'get_export_format':
            returned = get_export_format(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'request_render':
            returned = request_render(signal_dic['version_id'],
                                      signal_dic['work_env_id'],
                                      signal_dic['export_name'],
                                      signal_dic['comment'])
        elif signal_dic['function'] == 'add_export_version':
            returned = add_export_version(signal_dic['export_name'],
                                          signal_dic['files'],
                                          signal_dic['work_env_id'],
                                          signal_dic['version_id'],
                                          signal_dic['comment'])
        elif signal_dic['function'] == 'get_frame_range':
            returned = get_frame_range(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_image_format':
            returned = get_image_format()
        elif signal_dic['function'] == 'get_frame_rate':
            returned = get_frame_rate()
        elif signal_dic['function'] == 'get_user_folder':
            returned = get_user_folder()
        elif signal_dic['function'] == 'get_references':
            returned = get_references(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'modify_reference_LOD':
            returned = modify_reference_LOD(signal_dic['work_env_id'],
                                            signal_dic['LOD'],
                                            signal_dic['namespaces_list'])
        elif signal_dic['function'] == 'create_or_get_camera_work_env':
            returned = create_or_get_camera_work_env(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'create_or_get_rendering_work_env':
            returned = create_or_get_rendering_work_env(
                signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_hooks_folder':
            returned = project.get_hooks_folder()
        elif signal_dic['function'] == 'get_plugins_folder':
            returned = project.get_plugins_folder()
        elif signal_dic['function'] == 'get_string_variant_from_work_env_id':
            returned = get_string_variant_from_work_env_id(
                signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_local_path':
            returned = get_local_path()
        elif signal_dic['function'] == 'get_project_path':
            returned = get_project_path()
        elif signal_dic['function'] == 'request_video':
            returned = request_video(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'get_export_name_from_reference_namespace':
            returned = get_export_name_from_reference_namespace(
                signal_dic['reference_namespace'], signal_dic['work_env_id'])
        elif signal_dic['function'] == 'add_video':
            returned = add_video(signal_dic['work_env_id'],
                                 signal_dic['temp_dir'],
                                 signal_dic['frange'],
                                 signal_dic['version_id'],
                                 signal_dic['focal_lengths_dic'],
                                 signal_dic['comment'])
        elif signal_dic['function'] == 'screen_over_version':
            returned = screen_over_version(signal_dic['version_id'])
        elif signal_dic['function'] == 'get_stylesheet':
            returned = get_stylesheet()

        socket_utils.send_signal_with_conn(conn, returned)


def get_string_variant_from_work_env_id(work_env_id):
    work_env_row = project.get_work_env_data(work_env_id)
    string_variant = assets.instance_to_string(
        ('variant', work_env_row['variant_id']))
    return string_variant


def get_file(version_id):
    version_path = project.get_version_data(version_id, 'file_path')
    return version_path


def screen_over_version(version_id):
    success = assets.screen_over_version(version_id)
    return success


def add_version(work_env_id, comment):
    # Add a version using the 'assets' module and return the file path
    # of the new version
    if comment is None or comment == '':
        analyse_comment = False
    else:
        analyse_comment = True
    version_id = assets.add_version(
        work_env_id, comment=comment, analyse_comment=analyse_comment)
    if not version_id:
        return (None, None)
    version_path = project.get_version_data(version_id,
                                            'file_path')
    gui_server.refresh_ui()
    gui_server.save_popup(version_id)
    return (version_path, version_id)


def request_export(work_env_id, export_name):
    # Just return a temporary file name using the 'assets' module
    file_path = assets.request_export(work_env_id, export_name)
    return file_path


def get_export_format(work_env_id):
    extension = assets.get_default_extension(work_env_id)
    return extension


def request_video(work_env_id):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    return video.request_video(variant_id)


def add_video(work_env_id, temp_dir, frange, version_id, focal_lengths_dic=None, comment=''):
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    if comment is None or comment == '':
        analyse_comment = False
    else:
        analyse_comment = True
    string_asset = assets.instance_to_string(('work_version', version_id))
    video_path = video.add_video(variant_id, temp_dir, frange, string_asset,
                                 focal_lengths_dic, comment=comment, analyse_comment=analyse_comment)
    gui_server.refresh_ui()
    return video_path


def request_render(version_id, work_env_id, export_name, comment=''):
    # Just return a temporary file name using the 'assets' module
    render_directory = assets.request_render(
        version_id, work_env_id, export_name, comment=comment)
    gui_server.refresh_ui()
    return render_directory


def add_export_version(export_name, files, work_env_id, version_id, comment):
    # Add an export version using the 'assets' module and return the export_version_id
    # of the new export version
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    variant_row = project.get_variant_data(variant_id)
    if comment is None or comment == '':
        analyse_comment = False
    else:
        analyse_comment = True
    export_version_id = assets.add_export_version(
        export_name, files, variant_row['stage_id'], version_id, comment, analyse_comment=analyse_comment)
    export_dir = assets.get_export_version_path(export_version_id)
    gui_server.refresh_ui()
    return export_dir


def get_references(work_env_id):
    # Get the scene references
    return assets.get_references_files(work_env_id)


def get_frame_range(work_env_id):
    asset_row = assets.get_asset_data_from_work_env_id(work_env_id)
    if not asset_row:
        return
    return [asset_row['preroll'],
            asset_row['inframe'],
            asset_row['outframe'],
            asset_row['postroll']]


def modify_reference_LOD(work_env_id, LOD, namespaces_list):
    assets.modify_reference_LOD(work_env_id, LOD, namespaces_list)
    gui_server.refresh_team_ui()
    return


def get_image_format():
    return project.get_image_format()


def get_frame_rate():
    return project.get_frame_rate()


def get_user_folder():
    return user_vars._user_path_


def create_or_get_camera_work_env(work_env_id):
    return assets.create_or_get_camera_work_env(work_env_id)


def create_or_get_rendering_work_env(work_env_id):
    return assets.create_or_get_rendering_work_env(work_env_id)


def get_local_path():
    return user.user().get_local_path()


def get_project_path():
    return environment.get_project_path()


def get_export_name_from_reference_namespace(reference_namespace, work_env_id):
    reference_row = project.get_reference_by_namespace(
        work_env_id, reference_namespace)
    export_name = project.get_export_data(reference_row['export_id'], 'name')
    return export_name


def get_stylesheet():
    return ressources._stylesheet_
