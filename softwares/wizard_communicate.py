# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import sys
import logging

# Wizard modules
import socket_utils

# Handle ConnectionRefusedError in python 2
if sys.version_info[0] == 2:
    from socket import error as ConnectionRefusedError

logging.basicConfig(level=logging.INFO)


communicate_server_port_key = 'wizard_communicate_server_port'.upper()


def get_port():
    if communicate_server_port_key in os.environ.keys():
        return int(os.environ[communicate_server_port_key])
    else:
        logging.error('No communicate server port defined')
        return None


def add_version(work_env_id, comment=''):
    # Send a new version request to wizard
    # Wizard return a file path
    signal_dic = dict()
    signal_dic['function'] = 'add_version'
    signal_dic['comment'] = comment
    signal_dic['work_env_id'] = work_env_id
    file_path, version_id = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return file_path, version_id


def request_export(work_env_id, export_name):
    # Get a temporary export dir and file from wizard
    signal_dic = dict()
    signal_dic['function'] = 'request_export'
    signal_dic['work_env_id'] = work_env_id
    signal_dic['export_name'] = export_name
    file_path = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return file_path


def request_video(work_env_id):
    signal_dic = dict()
    signal_dic['function'] = 'request_video'
    signal_dic['work_env_id'] = work_env_id
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def add_video(work_env_id, temp_dir, frange, version_id, focal_lengths_dic=None, comment=''):
    signal_dic = dict()
    signal_dic['function'] = 'add_video'
    signal_dic['work_env_id'] = work_env_id
    signal_dic['temp_dir'] = temp_dir
    signal_dic['frange'] = frange
    signal_dic['version_id'] = version_id
    signal_dic['comment'] = comment
    signal_dic['focal_lengths_dic'] = focal_lengths_dic
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_export_format(work_env_id):
    # Get a temporary export dir and file from wizard
    signal_dic = dict()
    signal_dic['function'] = 'get_export_format'
    signal_dic['work_env_id'] = work_env_id
    file_path = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return file_path


def request_render(version_id, work_env_id, export_name, comment=''):
    # Get a temporary export dir and file from wizard
    signal_dic = dict()
    signal_dic['function'] = 'request_render'
    signal_dic['version_id'] = version_id
    signal_dic['work_env_id'] = work_env_id
    signal_dic['export_name'] = export_name
    signal_dic['comment'] = comment
    file_path = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return file_path


def add_export_version(export_name, files, work_env_id, version_id, comment=''):
    # Send a new export version request to wizard
    # Wizard return the export version id
    signal_dic = dict()
    signal_dic['function'] = 'add_export_version'
    signal_dic['export_name'] = export_name
    signal_dic['files'] = files
    signal_dic['version_id'] = version_id
    signal_dic['work_env_id'] = work_env_id
    signal_dic['comment'] = comment
    export_dir = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return export_dir


def get_references(work_env_id):
    # Request the scene references
    # Wizard return a references dic
    signal_dic = dict()
    signal_dic['function'] = 'get_references'
    signal_dic['work_env_id'] = work_env_id
    references_tuples = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return references_tuples


def get_frame_range(work_env_id):
    # Request the scene frame range
    # Return a [inframe, outframe] list
    signal_dic = dict()
    signal_dic['function'] = 'get_frame_range'
    signal_dic['work_env_id'] = work_env_id
    frame_range = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return frame_range


def get_image_format():
    # Request the project image format
    # Return a [width, height] list
    signal_dic = dict()
    signal_dic['function'] = 'get_image_format'
    image_format = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return image_format


def get_frame_rate():
    # Request the project image format
    # Return a [width, height] list
    signal_dic = dict()
    signal_dic['function'] = 'get_frame_rate'
    image_format = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return image_format


def get_user_folder():
    # Request the user folder ( Documents/Wizard )
    signal_dic = dict()
    signal_dic['function'] = 'get_user_folder'
    user_folder = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return user_folder


def modify_reference_LOD(work_env_id, LOD, namespaces_list):
    signal_dic = dict()
    signal_dic['function'] = 'modify_reference_LOD'
    signal_dic['work_env_id'] = work_env_id
    signal_dic['LOD'] = LOD
    signal_dic['namespaces_list'] = namespaces_list
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def create_or_get_camera_work_env(work_env_id):
    signal_dic = dict()
    signal_dic['function'] = 'create_or_get_camera_work_env'
    signal_dic['work_env_id'] = work_env_id
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def create_or_get_rendering_work_env(work_env_id):
    signal_dic = dict()
    signal_dic['function'] = 'create_or_get_rendering_work_env'
    signal_dic['work_env_id'] = work_env_id
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_file(version_id):
    signal_dic = dict()
    signal_dic['function'] = 'get_file'
    signal_dic['version_id'] = version_id
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_string_variant_from_work_env_id(work_env_id):
    signal_dic = dict()
    signal_dic['function'] = 'get_string_variant_from_work_env_id'
    signal_dic['work_env_id'] = work_env_id
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_hooks_folder():
    signal_dic = dict()
    signal_dic['function'] = 'get_hooks_folder'
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_plugins_folder():
    signal_dic = dict()
    signal_dic['function'] = 'get_plugins_folder'
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_local_path():
    # Send a new version request to wizard
    # Wizard return a file path
    signal_dic = dict()
    signal_dic['function'] = 'get_local_path'
    local_path = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return local_path


def get_project_path():
    # Send a new version request to wizard
    # Wizard return a file path
    signal_dic = dict()
    signal_dic['function'] = 'get_project_path'
    local_path = socket_utils.send_signal(
        ('localhost', get_port()), signal_dic)
    return local_path


def screen_over_version(version_id):
    signal_dic = dict()
    signal_dic['function'] = 'screen_over_version'
    signal_dic['version_id'] = version_id
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_export_name_from_reference_namespace(reference_namespace, work_env_id):
    signal_dic = dict()
    signal_dic['function'] = 'get_export_name_from_reference_namespace'
    signal_dic['reference_namespace'] = reference_namespace
    signal_dic['work_env_id'] = work_env_id
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned


def get_stylesheet():
    signal_dic = dict()
    signal_dic['function'] = 'get_stylesheet'
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned
