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
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class test(Thread):
    def __init__(self):
        super(test, self).__init__()
        hostname = 'localhost'
        port = 11112
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
                        print(json.loads(signal_as_str))
                        conn.send(json.dumps(["prout", "proutuututututiuj itj itjti jti jtij tij tij tij "]).encode('utf8'))
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.running = False

my_thread = test()
my_thread.start()

def send_signal(signal_as_str):
    # Send a signal to wizard
    # The signal_as_str is converted to json string
    # Before sending to wizard the signal 
    # will be encoded in utf-8 (bytes)
    try:
        host_name = 'localhost'
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.connect((host_name, 11112))
        server.settimeout(5.0)
        server.send(signal_as_str.encode('utf8'))
        returned = server.recv(2048).decode('utf8')
        print(json.loads(returned))
        server.close()
        return returned
    except ConnectionRefusedError:
        logger.error("No wizard local server found. Please verify if Wizard is openned")
        return None
    except socket.timeout:
        logger.error("Wizard has been too long to give a response, please retry.")
        return None

def make_request():
    for a in range(0,1000):
        send_signal(json.dumps(['aoi azopdkz opdkza opdkzaopdkapodkpozadk poazdk opzadkazpodk zaopdkzapo dzak dp', 'ooij', 22, 3422.22, 'pokopk']))