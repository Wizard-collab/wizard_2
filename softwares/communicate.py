from socket import *
import time
import traceback
import pickle
import logging
logging.basicConfig(level=logging.INFO)

def send_signal(signal_as_str):
    try:
        host_name = 'localhost'
        if host_name:
            server = socket(AF_INET, SOCK_STREAM)
            server.connect((host_name, 11111))
            server.settimeout(5.0)
            server.send(signal_as_str)
            returned = server.recv(2048)
            server.close()
            return returned
    except ConnectionRefusedError:
        logging.error("No wizard local server found. Please verify if Wizard is openned")
        return None
    except timeout:
        logging.error("Wizard has been too long to give a response, please retry.")
        return None

def add_version(work_env_id):
    signal_dic=dict()
    signal_dic['function'] = 'add_version'
    signal_dic['work_env_id'] = work_env_id
    signal_as_str = pickle.dumps(signal_dic)
    file_path = send_signal(signal_as_str)
    if file_path:
        file_path = pickle.loads(file_path)
    return file_path