# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import socket
import json
import traceback
import struct
import sys

import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Handle ConnectionRefusedError in python 2
if sys.version_info[0] == 2:
    from socket import error as ConnectionRefusedError

def get_connection(DNS, timeout=5.0, only_debug=False):
    connection = None
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        connection.connect((DNS[0], DNS[1]))
        return connection
    except ConnectionRefusedError:
        if only_debug:
            logger.debug("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        else:
            logger.error("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        if only_debug:
            logger.debug("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        else:    
            logger.error("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return None

def get_server(DNS):
    server = None
    server_address = None
    try:
        server_address = socket.gethostbyname(DNS[0])
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(DNS)
        server.listen(100)
    except ConnectionRefusedError:
        logger.debug("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return server, server_address

def send_bottle(DNS, msg_raw, timeout=0.01):
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(timeout)
        server.connect(DNS)
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        server.sendall(msg)
        return 1
    except ConnectionRefusedError:
        logger.debug("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    finally:
        if server is not None:
            server.close()

def send_signal(DNS, msg_raw, timeout=5.0):
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(timeout)
        server.connect(DNS)
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        server.sendall(msg)
        returned = recvall(server).decode('utf8')
        return json.loads(returned)
    except ConnectionRefusedError:
        logger.debug("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.error(str(traceback.format_exc()))
        return None
    finally:
        if server is not None:
            server.close()

def send_signal_with_conn(conn, msg_raw, only_debug = False):
    try:
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        conn.sendall(msg)
        return 1
    except ConnectionRefusedError:
        if only_debug:
            logger.debug("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        else:
            logger.error("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        if only_debug:
            logger.debug("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        else:    
            logger.error("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return None

def recvall(sock):
    try:
        raw_msglen = recvall_with_given_len(sock, 4)
        if not raw_msglen:
            return None
        if sys.version_info[0] == 2:
            raw_msglen = str(raw_msglen)
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall_with_given_len(sock, msglen)
    except ConnectionRefusedError:
        logger.debug("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None

def recvall_with_given_len(sock, n):
    try:
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    except ConnectionRefusedError:
        logger.debug("Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return data