# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from PyQt5.QtCore import pyqtSignal, QThread
import json

# Wizard modules
from wizard.core import socket_utils
from wizard.core import environment

class team_client(QThread):

    team_connection_status_signal = pyqtSignal(bool)
    refresh_signal = pyqtSignal(int)

    def __init__(self):
        super(team_client, self).__init__()
        self.create_conn()

    def create_conn(self):
        self.running = True
        team_dns = environment.get_team_dns()
        if team_dns is not None:
            self.conn = socket_utils.get_connection(team_dns)
        else:
            self.conn = None
        if self.conn is not None:
            self.init_conn()

    def init_conn(self):
        signal_dic = dict()
        signal_dic['type'] = 'new_client'
        signal_dic['user_name'] = environment.get_user()
        socket_utils.send_signal_with_conn(self.conn, signal_dic)

    def stop(self):
        if self.conn is not None:
            self.conn.close()
        self.running = False

    def refresh_team(self):
        if self.conn is not None:
            signal_dic = dict()
            signal_dic['type'] = 'refresh_team'
            if not socket_utils.send_signal_with_conn(self.conn, signal_dic, only_debug=True):
                self.conn.close()
                self.conn = None
                self.running = False

    def run(self):
        self.create_conn()
        self.team_connection_status_signal.emit(True)
        while self.conn is not None and self.running is True:
            raw_data = socket_utils.recvall(self.conn)
            if raw_data is not None:
                try:
                    data = json.loads(raw_data)
                    self.analyse_signal(data)
                except json.decoder.JSONDecodeError:
                    logger.debug("cannot read json data")
        self.team_connection_status_signal.emit(False)

    def analyse_signal(self, data):
        if data['type'] == 'refresh_team':
            self.refresh_signal.emit(1)

def try_connection(DNS):
    signal_dic = dict()
    signal_dic['type'] = 'test_conn'
    return socket_utils.send_bottle(DNS, signal_dic)
