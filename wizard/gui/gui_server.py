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
from wizard.vars import ressources
from wizard.core import environment
from wizard.core import socket_utils
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

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
    refresh_team_signal = pyqtSignal(int)
    restart_signal = pyqtSignal(int)
    tooltip_signal = pyqtSignal(str)
    stdout_signal = pyqtSignal(tuple)
    export_version_focus_signal = pyqtSignal(object)
    focus_instance_signal = pyqtSignal(object)
    save_popup_signal = pyqtSignal(int)
    raise_ui_signal = pyqtSignal(int)
    popup_signal = pyqtSignal(object)

    def __init__(self):
        super(gui_server, self).__init__()

        self.streamHandler = streamHandler()
        #sys.stdout = self.streamHandler
        #sys.stderr = self.streamHandler

        self.port = socket_utils.get_port('localhost')
        environment.set_gui_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(('localhost', self.port))
        self.running = True

        self.connect_functions()

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn)
                    if signal_as_str:
                        self.analyse_signal(signal_as_str, conn)
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def stop(self):
        self.server.close()
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        # The signal_as_str is already decoded ( from utf8 )
        # The incoming signal needs to be a json string
        returned = None
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'refresh':
            self.refresh_signal.emit(1)
        if signal_dic['function'] == 'restart':
            self.restart_signal.emit(1)
        elif signal_dic['function'] == 'tooltip':
            self.tooltip_signal.emit(signal_dic['tooltip'])
        elif signal_dic['function'] == 'focus_instance':
            self.focus_instance_signal.emit(signal_dic['instance_tuple'])
            self.raise_ui_signal.emit(1)
        elif signal_dic['function'] == 'export_version_focus':
            self.export_version_focus_signal.emit(signal_dic['export_version_id'])
            self.raise_ui_signal.emit(1)
        elif signal_dic['function'] == 'refresh_team':
            self.refresh_team_signal.emit(1)
        elif signal_dic['function'] == 'save_popup':
            self.save_popup_signal.emit(signal_dic['version_id'])
        elif signal_dic['function'] == 'raise':
            self.raise_ui_signal.emit(1)
        elif signal_dic['function'] == 'popup':
            self.popup_signal.emit(signal_dic['data'])

    def connect_functions(self):
        self.streamHandler.stream.connect(self.stdout_signal.emit)

def try_connection():
    conn = socket_utils.get_connection(_DNS_, timeout=0.1, only_debug=True)
    if conn:
        conn.close()
        return 1
    else:
        return None

def refresh_ui():
    refresh_team_ui()
    signal_dic = dict()
    signal_dic['function'] = 'refresh'
    send_signal(signal_dic)

def refresh_team_ui():
    signal_dic = dict()
    signal_dic['function'] = 'refresh_team'
    send_signal(signal_dic)

def restart_ui():
    signal_dic = dict()
    signal_dic['function'] = 'restart'
    send_signal(signal_dic)

def save_popup(version_id):
    signal_dic = dict()
    signal_dic['function'] = 'save_popup'
    signal_dic['version_id'] = version_id
    send_signal(signal_dic)

def custom_popup(title, msg, icon=ressources._info_icon_, profile_picture=None):
    signal_dic = dict()
    signal_dic['function'] = 'popup'
    signal_dic['data'] = [title, msg, icon, profile_picture]
    send_signal(signal_dic)

def tooltip(tooltip):
    signal_dic = dict()
    signal_dic['function'] = 'tooltip'
    signal_dic['tooltip'] = tooltip
    send_signal(signal_dic)

def focus_instance(instance_tuple):
    signal_dic = dict()
    signal_dic['function'] = 'focus_instance'
    signal_dic['instance_tuple'] = instance_tuple
    send_signal(signal_dic)

def focus_export_version(export_version_id):
    signal_dic = dict()
    signal_dic['function'] = 'export_version_focus'
    signal_dic['export_version_id'] = export_version_id
    send_signal(signal_dic)

def raise_ui():
    signal_dic = dict()
    signal_dic['function'] = 'raise'
    send_signal(signal_dic)

def send_signal(signal_dic):
    socket_utils.send_bottle(('localhost', environment.get_gui_server_port()), signal_dic, timeout=0.5)

