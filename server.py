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
import sys
from threading import *
import time
import traceback
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import struct

# create logger
logger = logging.getLogger('WIZARD-SERVER')
logger.setLevel(logging.DEBUG)

log_file = "wizard_server.log"
# create file handler and set level to debug
file_handler = RotatingFileHandler(log_file, mode='a', maxBytes=1000000, backupCount=1000, encoding=None, delay=False)
# create console handler and set level to debug
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to handlers
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
# add handlers to logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.info("Python : " + str(sys.version))

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

def recvall(sock):
    try:
        raw_msglen = recvall_with_given_len(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall_with_given_len(sock, msglen)
    except ConnectionRefusedError:
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
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
        logger.debug(f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.debug(f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return data

class server(Thread):
    def __init__(self):
        super(server, self).__init__()
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)
        port = 50333
        logger.info("Starting server on : '" + str(ip_address) + "'")
        logger.info("Default port : '" + str(port) + "'")
        self.server, self.server_adress = get_server((ip_address, port))
        logger.info("Server started")
        self.client_ids = dict()

    def run(self):
        while True:
            try:
                conn, addr = self.server.accept()
                entry_message = recvall(conn)
                self.analyse_signal(entry_message, conn, addr)
            except:
                logger.error(str(traceback.format_exc()))
                continue
        
    def analyse_signal(self, msg_raw, conn, addr):
        data = json.loads(msg_raw)
        print(data)
        if data['type'] == 'test_conn':
            logger.info('test_conn')
        elif data['type'] == 'new_client':
            self.add_client(data['user_name'], conn, addr, data['project'])

    def add_client(self, user_name, conn, addr, project):
        if user_name not in self.client_ids.keys():
            client_dic = dict()
            client_dic['user_name'] = user_name
            client_dic['conn'] = conn
            client_dic['addr'] = addr
            client_dic['project'] = project
            self.client_ids[user_name]=client_dic

            Thread(target=self.clientThread, args=(user_name, conn, addr, project)).start()
            logger.info("New client : {}, {}, {}".format(user_name, addr, project))
            signal_dic = dict()
            signal_dic['type'] = 'new_user'
            signal_dic['user_name'] = user_name
            signal_dic['project'] = project
            self.broadcast(signal_dic, self.client_ids[user_name])
            self.send_users_to_new_client(client_dic)
        else:
            conn.close()
            logger.info("Client already exists : {}, {}, {}".format(user_name, addr, project))

    def send_users_to_new_client(self, client_dic):
        for client in self.client_ids.keys():
            if self.client_ids[client]['user_name'] != client_dic['user_name']:
                signal_dic = dict()
                signal_dic['type'] = 'new_user'
                signal_dic['user_name'] = self.client_ids[client]['user_name']
                signal_dic['project'] = self.client_ids[client]['project']
                send_signal_with_conn(client_dic['conn'], signal_dic)

    def clientThread(self, user_name, conn, addr, project):
        client_dic = dict()
        client_dic['user_name'] = user_name
        client_dic['conn'] = conn
        client_dic['addr'] = addr
        client_dic['project'] = project
        running = True
        while running:
            try:
                raw_data = recvall(client_dic['conn'])
                if raw_data is not None:
                    data = json.loads(raw_data)
                    self.broadcast(data, client_dic)
                else:
                    if conn is not None:
                        self.remove_client(client_dic)
                        running = False
            except:
                logger.error(str(traceback.format_exc()))
                continue           

    def broadcast(self, data, client_dic):
        logger.debug("Broadcasting : " + str(data))
        for client in self.client_ids.keys(): 
            if client != client_dic['user_name']:
                if not send_signal_with_conn(self.client_ids[client]['conn'], data):
                    self.remove_client(self.client_ids[client])

    def remove_client(self, client_dic): 
        if client_dic['user_name'] in self.client_ids.keys(): 
            logger.info("Removing client : {}, {}, {}".format(client_dic['user_name'], client_dic['addr'], client_dic['project']))
            del self.client_ids[client_dic['user_name']]
            client_dic['conn'].close()
            signal_dic = dict()
            signal_dic['type'] = 'remove_user'
            signal_dic['user_name'] = client_dic['user_name']
            signal_dic['project'] = client_dic['project']
            self.broadcast(signal_dic, client_dic)

if __name__ == "__main__":
    try:
        server = server()
        server.daemon = True
        server.start()
        print('Press Ctrl+C to quit...')
        while 1:time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping server...')
        raise SystemExit
        sys.exit()

