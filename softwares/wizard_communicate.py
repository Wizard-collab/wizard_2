# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
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

_DNS_ = ('localhost', 11111)

def add_version(work_env_id):
    # Send a new version request to wizard
    # Wizard return a file path 
    signal_dic=dict()
    signal_dic['function'] = 'add_version'
    signal_dic['work_env_id'] = work_env_id
    file_path = socket_utils.send_signal(_DNS_, signal_dic)
    return file_path

def request_export(work_env_id, export_name):
    # Get a temporary export dir and file from wizard
    signal_dic=dict()
    signal_dic['function'] = 'request_export'
    signal_dic['work_env_id'] = work_env_id
    signal_dic['export_name'] = export_name
    file_path = send_signal(_DNS_, signal_dic)
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
    export_version_id = send_signal(_DNS_, signal_dic)
    return export_version_id

def get_references(work_env_id):
    # Request the scene references
    # Wizard return a references dic
    signal_dic=dict()
    signal_dic['function'] = 'references'
    signal_dic['work_env_id'] = work_env_id
    references_tuples = socket_utils.send_signal(_DNS_, signal_dic)
    return references_tuples