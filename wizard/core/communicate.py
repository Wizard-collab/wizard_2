# coding: utf-8

# Python modules
import socket
import sys
from threading import *
import time
import traceback

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

class communicate_server(thread):
    def __init__(self):
        super(communicate_server, self).__init__()
        hostname = 'localhost'
        self.server_address = socket.gethostbyname(hostname)
        port = 11111
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
                        self.analyse_signal(signal_as_str)
                        #time.sleep(0.05)
            except:
                logging.error(str(traceback.format_exc()))
                continue