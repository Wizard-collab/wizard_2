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
from wizard.core import assets
from wizard.core import project
from wizard.core import logging
logging = logging.get_logger(__name__)

class communicate_server(Thread):
    def __init__(self):
        super(communicate_server, self).__init__()
        hostname = 'localhost'
        port = 11111
        self.server_address = socket.gethostbyname(hostname)
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((hostname, port))
        self.server.listen(100) 
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
                logging.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        # The signal_as_str is already decoded ( from utf8 )
        # The incoming signal needs to be a json string
        returned = None
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'add_version':
            returned = self.add_version(signal_dic['work_env_id'])

        conn.send(json.dumps(returned).encode('utf8'))

def add_version(work_env_id):
    # Add a version using the wizard core and return the file path 
    # of the new version
    version_id = assets.add_version(work_env_id)
    version_path = project.project().get_version_data(version_id,
                                                    'file_path')
    return version_path
