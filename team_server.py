# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

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
            self.add_client(data['user_name'], conn, addr)

    def add_client(self, user_name, conn, addr):
        self.client_ids[user_name] = user_name
        Thread(target=self.clientThread, args=(conn, user_name, addr)).start()
        logger.info("New client : {}, {}".format(user_name, addr))

    def clientThread(self, conn, user_name, addr):
        running = True
        while running:
            try:
                raw_data = recvall(conn)
                if raw_data is not None:
                    data = json.loads(raw_data)
                    print(data)
                    print(user_name)
                    print(conn)
                    print(addr)
                else:
                    if conn is not None:
                        self.remove_client(conn, user_name, addr)
                        running = False
            except:
                logger.error(str(traceback.format_exc()))
                continue           

    def broadcast(self, message, conn):
        logger.debug("Broadcasting : " + str(message))
        for client in self.list_of_clients: 
            try: 
                client[0].send(message)
            except:
                client[0].close() 
                self.remove(client)

    def remove_client(self, conn, user_name, addr): 
        if user_name in self.client_ids.keys(): 
            logger.info("Removing client : {}, {}".format(user_name, addr))
            del self.client_ids[user_name]
            conn.close()

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

