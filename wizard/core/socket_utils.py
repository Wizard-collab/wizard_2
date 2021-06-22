# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import socket
import json
import traceback

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

def recvall(sock):
    BUFF_SIZE = 4096 # 4 KiB
    data = b''
    while True:
        part = sock.recv(BUFF_SIZE)
        data += part
        if len(part) < BUFF_SIZE:
            # either 0 or end of data
            break
    return data

def get_server(DNS):
    server_address = socket.gethostbyname(DNS[0])
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind(DNS)
    server.listen(100)
    return server, server_address

def send_signal(DNS, msg_raw):
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect(DNS)
        server.settimeout(5.0)
        server.send(json.dumps(msg_raw).encode('utf8'))
        returned = recvall(server).decode('utf8')
        return json.loads(returned)
    except ConnectionRefusedError:
        logging.error(f"Socket connection refused : host={host}, port={port}")
        return None
    except socket.timeout:
        logging.error(f"Socket timeout (5s) : host={host}, port={port}")
        return None
    except:
        logging.error(str(traceback.format_exc()))
    finally:
        if server is not None:
            server.close()