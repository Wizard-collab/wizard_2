# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from threading import *

# Wizard modules
from wizard.core import socket_utils
from wizard.core import environment

class team_client(Thread):
    def __init__(self):
        super(team_client, self).__init__()
        self.running = True
        self.conn = socket_utils.get_connection(environment.get_team_dns())
        if self.conn is not None:
            self.init_conn()

    def init_conn(self):
        signal_dic = dict()
        signal_dic['type'] = 'new_client'
        signal_dic['user_name'] = environment.get_user()
        socket_utils.send_signal_with_conn(self.conn, signal_dic)

    def stop(self):
        self.running = False

    def refresh_team(self):
        if self.conn is not None:
            signal_dic = dict()
            signal_dic['type'] = 'refresh_team'
            socket_utils.send_signal_with_conn(self.conn, signal_dic)

    def run(self):
        while self.conn is not None and self.running is True:
            raw_data = socket_utils.recvall(self.conn)
            if raw_data is not None:
                try:
                    data = json.loads(raw_data)
                    print(data)
                    #self.analyse_signal(data)
                except json.decoder.JSONDecodeError:
                    logger.debug("cannot read json data")

def try_connection(DNS):
    signal_dic = dict()
    signal_dic['type'] = 'test_conn'
    return socket_utils.send_bottle(DNS, signal_dic)
