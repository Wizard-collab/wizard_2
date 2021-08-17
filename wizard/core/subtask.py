# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module manage substasks

# Python modules
from threading import Thread
import subprocess
import time
import json
import shlex
import os
import traceback

# Wizard modules
from wizard.core import socket_utils
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

_DNS_ = ('localhost', 10231)

class subtask(Thread):
    def __init__(self, cmd=None, env=None, cwd=None):
        super(subtask, self).__init__()
        self.process_id = str(time.time())
        self.process = None
        self.command = cmd
        if env is None:
            self.env = os.environ.copy()
        else:
            self.env = env
        self.cwd = cwd
        self.running = False
        self.out = ''

    def set_command(self, command):
        self.command = command

    def set_env(self, env):
        if env is not None:
            if type(env)==dict:
                self.env = env

    def set_cwd(self, cwd):
        self.cwd = cwd

    def add_python_buffer_env(self):
        if "PYTHONUNBUFFERED" not in self.env:
            self.env["PYTHONUNBUFFERED"] = "1"

    def check_output(self):
        while self.running:
            output = self.process.stdout.readline()
            if self.process.poll() is not None:
                time.sleep(0.1)
                self.communicate_thread.send_signal([self.process_id, 'status', 'Done'])
                self.communicate_thread.send_signal([self.process_id, 'percent', 100])
                self.running = False
                break
            if output:
                out = output.strip().decode('utf-8')
                self.analyse_signal(out)

    def analyse_signal(self, out):
        if 'wizard_task_percent:' in out:
            percent = float(out.split(':')[-1])
            self.communicate_thread.send_signal([self.process_id, 'percent', percent])
        elif 'wizard_task_name:' in out:
            task = out.split(':')[-1]
            self.communicate_thread.send_signal([self.process_id, 'current_task', task])
        else:
            self.out+='\n'+out
            self.communicate_thread.send_signal([self.process_id, 'stdout', out])

    def write(self, stdin):
        try:
            stdin = (stdin+'\n').encode('utf-8')
            self.process.stdin.write(stdin)
            self.process.stdin.flush()
        except:
            self.communicate_thread.send_signal([self.process_id, 'stdout', str(traceback.format_exc())])

    def kill(self):
        if self.running == True:
            if self.process is not None:
                self.process.kill()
                self.communicate_thread.send_signal([self.process_id, 'status', 'Killed'])
            self.running = False

    def run(self):
        try:
            self.running = True

            self.communicate_thread = communicate_thread(self)
            self.communicate_thread.start()
            time.sleep(0.1)

            self.communicate_thread.send_signal([self.process_id, 'status', 'Running'])
            self.add_python_buffer_env()
            time.sleep(0.1)

            self.process = subprocess.Popen(args = shlex.split(self.command), env=self.env, cwd=self.cwd,
                                            stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.PIPE)

            self.check_output()
            self.running = False
            time.sleep(0.1)
            self.communicate_thread.stop()
        except:
            self.communicate_thread.send_signal([self.process_id, 'stdout', str(traceback.format_exc())])

def send_signal(signal_list):
    socket_utils.send_bottle(_DNS_, signal_list, 0.001)

class communicate_thread(Thread):
    def __init__(self, parent = None):
        super(communicate_thread, self).__init__()
        self.parent = parent
        self.running = True
        self.conn = socket_utils.get_connection(_DNS_)
        if self.conn is not None:
            socket_utils.send_signal_with_conn(self.conn, self.parent.process_id)

    def stop(self):
        self.running = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def run(self):
        while self.conn is not None and self.running is True:
            raw_data = socket_utils.recvall(self.conn)
            if raw_data is not None:
                try:
                    data = json.loads(raw_data)
                    self.analyse_signal(data)
                except json.decoder.JSONDecodeError:
                    logger.debug("cannot read json data")
            else:
                if self.conn is not None:
                    self.conn.close()
                self.running = False
                break

    def analyse_signal(self, data):
        if data == 'kill':
            self.parent.kill()

    def send_signal(self, signal_list):
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, signal_list, only_debug=True):
                self.conn.close()
                self.conn = None
