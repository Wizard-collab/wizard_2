# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to handle third party softwares commands
# For example if you want to save a version within a 
# Maya, the software plugin sends a socket signal
# here and waits for a return ( also socket signal )

# It roughly is a lan access to the wizard core functions

# Python modules
from PyQt5 import QtCore
from PyQt5.QtCore import QThread, pyqtSignal
import socket
import sys
import time
import traceback
import json

# Wizard modules
from wizard.core import socket_utils
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

_DNS_ = ('localhost', 11113)

class streamHandler(QtCore.QObject):

    stream = pyqtSignal(tuple)

    def __init__(self, parent=None):
        super(streamHandler, self).__init__(parent)

    def write(self, stream):
        self.stream.emit(('STDOUT', str(stream)))
        real_write = type(sys.__stdout__).write
        real_write(sys.__stdout__, stream)

class gui_server(QThread):

    refresh_signal = pyqtSignal(int)
    tooltip_signal = pyqtSignal(str)
    stdout_signal = pyqtSignal(tuple)
    tree_focus_signal = pyqtSignal(object)

    def __init__(self):
        super(gui_server, self).__init__()

        self.streamHandler = streamHandler()
        #sys.stdout = self.streamHandler
        #sys.stderr = self.streamHandler

        self.server, self.server_address = socket_utils.get_server(_DNS_)
        self.running = True

        self.connect_functions()

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = conn.recv(2048).decode('utf8')
                    if signal_as_str:
                        self.analyse_signal(signal_as_str, conn)
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        # The signal_as_str is already decoded ( from utf8 )
        # The incoming signal needs to be a json string
        returned = None
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'refresh':
            self.refresh_signal.emit(1)
        elif signal_dic['function'] == 'tooltip':
            self.tooltip_signal.emit(signal_dic['tooltip'])
        elif signal_dic['function'] == 'tree_focus':
            self.tree_focus_signal.emit(signal_dic['instance_tuple'])

    def connect_functions(self):
        self.streamHandler.stream.connect(self.stdout_signal.emit)

def refresh_ui():
	signal_dic = dict()
	signal_dic['function'] = 'refresh'
	socket_utils.send_bottle(_DNS_, signal_dic, timeout=0.01)

def tooltip(tooltip):
    signal_dic = dict()
    signal_dic['function'] = 'tooltip'
    signal_dic['tooltip'] = tooltip
    socket_utils.send_bottle(_DNS_, signal_dic, timeout=0.01)

def tree_focus_instance(instance_tuple):
    signal_dic = dict()
    signal_dic['function'] = 'tree_focus'
    signal_dic['instance_tuple'] = instance_tuple
    socket_utils.send_bottle(_DNS_, signal_dic, timeout=0.01)