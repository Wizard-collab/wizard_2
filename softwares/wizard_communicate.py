# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import sys
import socket
import time
import traceback
import json
import logging
logging.basicConfig(level=logging.INFO)

# Handle ConnectionRefusedError in python 2
if sys.version_info[0] == 2:
    from socket import error as ConnectionRefusedError

def send_signal(signal_as_str):
    # Send a signal to wizard
    # The signal_as_str is converted to json string
    # Before sending to wizard the signal 
    # will be encoded in utf-8 (bytes)
    try:
        host_name = 'localhost'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host_name, 11111))
        server.settimeout(5.0)
        server.send(signal_as_str.encode('utf8'))
        returned = server.recv(2048).decode('utf8')
        server.close()
        return returned
    except ConnectionRefusedError:
        logging.error("No wizard local server found. Please verify if Wizard is openned")
        return None
    except socket.timeout:
        logging.error("Wizard has been too long to give a response, please retry.")
        return None

def add_version(work_env_id):
    # Send a new version request to wizard
    # Wizard return a file path 
    signal_dic=dict()
    signal_dic['function'] = 'add_version'
    signal_dic['work_env_id'] = work_env_id
    signal_as_str = json.dumps(signal_dic)
    file_path = send_signal(signal_as_str)
    if file_path:
        file_path = json.loads(file_path)
    return file_path