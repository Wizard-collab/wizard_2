# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import sys
import socket
import time
import traceback
import json
import struct
import logging
logging.basicConfig(level=logging.INFO)

# Wizard modules
import socket_utils

# Handle ConnectionRefusedError in python 2
if sys.version_info[0] == 2:
    from socket import error as ConnectionRefusedError

communicate_server_port_key = 'wizard_communicate_server_port'.upper()

def get_port():
    if communicate_server_port_key in os.environ.keys():
        return int(os.environ[communicate_server_port_key])
    else:
        logging.error('No communicate server port defined')
        return None

def add_version(work_env_id):
    # Send a new version request to wizard
    # Wizard return a file path 
    signal_dic=dict()
    signal_dic['function'] = 'add_version'
    signal_dic['work_env_id'] = work_env_id
    file_path, version_id = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return file_path, version_id

def request_export(work_env_id, export_name):
    # Get a temporary export dir and file from wizard
    signal_dic=dict()
    signal_dic['function'] = 'request_export'
    signal_dic['work_env_id'] = work_env_id
    signal_dic['export_name'] = export_name
    file_path = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return file_path

def add_export_version(export_name, files, version_id, comment=''):
    # Send a new export version request to wizard
    # Wizard return the export version id 
    signal_dic=dict()
    signal_dic['function'] = 'add_export_version'
    signal_dic['export_name'] = export_name
    signal_dic['files'] = files
    signal_dic['version_id'] = version_id
    signal_dic['comment'] = comment
    export_dir = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return export_dir

def get_references(work_env_id):
    # Request the scene references
    # Wizard return a references dic
    signal_dic=dict()
    signal_dic['function'] = 'get_references'
    signal_dic['work_env_id'] = work_env_id
    references_tuples = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return references_tuples

def get_frame_range(work_env_id):
    # Request the scene frame range
    # Return a [inframe, outframe] list
    signal_dic=dict()
    signal_dic['function'] = 'get_frame_range'
    signal_dic['work_env_id'] = work_env_id
    frame_range = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return frame_range

def get_image_format():
    # Request the project image format
    # Return a [width, height] list
    signal_dic=dict()
    signal_dic['function'] = 'get_image_format'
    image_format = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return image_format

def get_user_folder():
    # Request the user folder ( Documents/Wizard )
    signal_dic=dict()
    signal_dic['function'] = 'get_user_folder'
    user_folder = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return user_folder

def modify_modeling_reference_LOD(work_env_id, LOD):
    signal_dic=dict()
    signal_dic['function'] = 'modify_modeling_reference_LOD'
    signal_dic['work_env_id'] = work_env_id
    signal_dic['LOD'] = LOD
    returned = socket_utils.send_signal(('localhost', get_port()), signal_dic)
    return returned