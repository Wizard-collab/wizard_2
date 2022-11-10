# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This file is part of Wizard

# MIT License

# Copyright (c) 2021 Leo brunel

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

# Python modules
import socket
import json
import traceback
import struct
import logging

logger = logging.getLogger(__name__)

def get_connection(DNS, timeout=5.0, only_debug=False):
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        connection.connect((DNS[0], DNS[1]))
        return connection
    except ConnectionRefusedError:
        if only_debug:
            logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        else:
            logger.info(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        if only_debug:
            logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        else:    
            logger.info(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return

def get_port(ip_adress):
    port = 11111
    while get_connection(('localhost', port),
                            timeout=0.02,
                            only_debug=True):
        port+=1
    return port

def get_server(DNS):
    try:
        server_address = socket.gethostbyname(DNS[0])
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(DNS)
        server.listen(100)
        return server, server_address
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None, None
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return None, None
    except:
        logger.debug(str(traceback.format_exc()))
        return None, None

def send_bottle(DNS, msg_raw, timeout=0.01):
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(timeout)
        server.connect((DNS[0], DNS[1]))
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        server.sendall(msg)
        return 1
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        logger.debug(str(traceback.format_exc()))
        return
    finally:
        if server:
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
        returned_b = recvall(server)
        if returned_b:
            return json.loads(returned_b.decode('utf8'))
        else:
            return
    except ConnectionRefusedError:
        logger.error(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        logger.error(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        logger.error(str(traceback.format_exc()))
        return
    finally:
        if server:
            server.close()

def send_signal_with_conn(conn, msg_raw, only_debug = False):
    try:
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        conn.sendall(msg)
        return 1
    except ConnectionRefusedError:
        if only_debug:
            logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        else:
            logger.error(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        if only_debug:
            logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        else:    
            logger.error(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return

def recvall(sock):
    try:
        raw_msglen = recvall_with_given_len(sock, 4)
        if not raw_msglen:
            return
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall_with_given_len(sock, msglen)
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        logger.debug(str(traceback.format_exc()))
        return

def recvall_with_given_len(sock, n):
    try:
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return
            data.extend(packet)
        return data
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        logger.debug(str(traceback.format_exc()))
        return
