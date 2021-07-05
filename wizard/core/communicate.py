# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to handle third party softwares commands
# For example if you want to save a version within a 
# Maya, the software plugin sends a socket signal
# here and waits for a return ( also socket signal )

# It roughly is a lan access to the wizard core functions

# Python modules
import socket
import sys
from threading import Thread
import time
import traceback
import json

# Wizard modules
from wizard.core import socket_utils
from wizard.core import assets
from wizard.core import project
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

_DNS_ = ('localhost', 11111)

class communicate_server(Thread):
    def __init__(self):
        super(communicate_server, self).__init__()
        self.server, self.server_address = socket_utils.get_server(_DNS_)
        self.running = True

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = conn.recv(2048).decode('utf8')
                    if signal_as_str:
                        self.analyse_signal(signal_as_str, conn)
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        # The signal_as_str is already decoded ( from utf8 )
        # The incoming signal needs to be a json string
        returned = None
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'add_version':
            returned = add_version(signal_dic['work_env_id'])
        elif signal_dic['function'] == 'request_export':
            returned = request_export(signal_dic['work_env_id'],
                                        signal_dic['export_name'])
        elif signal_dic['function'] == 'add_export_version':
            returned = add_export_version(signal_dic['export_name'],
                                        signal_dic['files'],
                                        signal_dic['version_id'], 
                                        signal_dic['comment'])

        conn.send(json.dumps(returned).encode('utf8'))

def add_version(work_env_id):
    # Add a version using the 'assets' module and return the file path 
    # of the new version
    version_id = assets.add_version(work_env_id)
    version_path = project.get_version_data(version_id,
                                                    'file_path')
    return version_path

def request_export(work_env_id, export_name):
    # Just return a temporary file name using the 'assets' module
    file_path = assets.request_export(work_env_id, export_name)
    return file_path

def add_export_version(export_name, files, version_id, comment):
    # Add an export version using the 'assets' module and return the export_version_id 
    # of the new export version
    export_version_id = assets.add_export_version(export_name, files, version_id, comment)
    return export_version_id
