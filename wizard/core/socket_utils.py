# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import socket
import json
import traceback

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

def recvall(sock):
    data = None
    try:
        BUFF_SIZE = 4096 # 4 KiB
        data = b''
        while True:
            part = sock.recv(BUFF_SIZE)
            data += part
            if len(part) < BUFF_SIZE:
                # either 0 or end of data
                break
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return data

def get_connection(DNS, timeout=5.0):
    connection = None
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        connection.connect(DNS)
        return connection
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return None
    except:
        logger.debug(str(traceback.format_exc()))
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
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
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
        server.send(json.dumps(msg_raw).encode('utf8'))
        return 1
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
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
        server.send(json.dumps(msg_raw).encode('utf8'))
        returned = recvall(server).decode('utf8')
        return json.loads(returned)
    except ConnectionRefusedError:
        logger.error(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.error(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return None
    except:
        logger.error(str(traceback.format_exc()))
        return None
    finally:
        if server is not None:
            server.close()

def send_signal_with_conn(conn, msg_raw, only_debug = False):
    try:
        conn.send(json.dumps(msg_raw).encode('utf8'))
        return 1
    except ConnectionRefusedError:
        if only_debug:
            logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        else:
            logger.error(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        if only_debug:
            logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        else:    
            logger.error(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return None
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return None