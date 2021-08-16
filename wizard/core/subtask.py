# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module manage substasks

# Python modules
from threading import Thread
import subprocess
import time
import shlex
import os
import traceback

# Wizard modules
from wizard.core import socket_utils
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

_DNS_ = ('localhost', 10231)

class subtask_thread(Thread):

    def __init__(self, cmd=None, env=None, cwd=None):
        super(subtask_thread, self).__init__()

        self.process_id = str(time.time())

        self.process = None
        self.clock_thread = clock_thread(self.process_id)
        self.command = cmd
        if env is None:
            self.env = os.environ.copy()
        else:
            self.env = env
        self.cwd = cwd
        self.running = False

    def set_command(self, command):
        self.command = command

    def set_env(self, env):
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
                send_signal([self.process_id, 'status', 'Done'])
                self.running = False
                break
            if output:
                out = output.strip().decode('utf-8')
                self.analyse_signal(out)

    def analyse_signal(self, out):
        if 'wizard_task_percent:' in out:
            percent = float(out.split(':')[-1])
            send_signal([self.process_id, 'percent', percent])
        elif 'wizard_task_name:' in out:
            task = out.split(':')[-1]
            send_signal([self.process_id, 'current_task', task])
        else:
            send_signal([self.process_id, 'stdout', out])

    def write(self, stdin):
        try:
            stdin = (stdin+'\n').encode('utf-8')
            self.process.stdin.write(stdin)
            self.process.stdin.flush()
        except:
            send_signal([self.process_id, 'stdout', str(traceback.format_exc())])

    def kill(self):
        self.clock_thread.stop()
        if self.running == True:
            self.running = False
        if self.process is not None:
            self.process.kill()
            send_signal([self.process_id, 'status', 'Killed'])

    def run(self):
        try:
            self.running = True
            send_signal([self.process_id, 'status', 'Running'])
            self.add_python_buffer_env()
            self.clock_thread.start()
            self.process = subprocess.Popen(args = shlex.split(self.command), env=self.env, cwd=self.cwd,
                                            stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.PIPE)
            self.check_output()
            self.running = False
            self.clock_thread.stop()
        except:
            send_signal([self.process_id, 'stdout', str(traceback.format_exc())])

class clock_thread(Thread):

    def __init__(self, process_id):
        super(clock_thread, self).__init__()
        self.process_id = process_id
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        time_count = 0
        send_signal([self.process_id, 'time', time_count])
        while self.running:
            time.sleep(1)
            time_count += 1
            send_signal([self.process_id, 'time', time_count])

def send_signal(signal_list):
    socket_utils.send_bottle(_DNS_, signal_list)
