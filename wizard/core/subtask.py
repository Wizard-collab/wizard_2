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

# This module manage substasks

# Python modules
from threading import Thread
import subprocess
import time
import json
import shlex
import os
import traceback
import sys
import logging

# Wizard modules
from wizard.vars import user_vars
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import socket_utils

logger = logging.getLogger(__name__)

_DNS_ = ('localhost', 10231)

class subtask(Thread):
    def __init__(self, cmd=None, pycmd=None, env=None, cwd=None, print_stdout=False):
        super(subtask, self).__init__()
        self.process_id = str(time.time())
        self.process = None
        self.command = cmd
        self.pycmd = pycmd
        if env is None:
            self.env = os.environ.copy()
        else:
            self.env = env
        self.cwd = cwd
        self.print_stdout = print_stdout
        self.running = False
        self.out = ''

    def set_print_stdout(self):
        self.print_stdout=True

    def set_command(self, command):
        self.command = command

    def set_pycmd(self, pycmd):
        self.pycmd = pycmd

    def set_env(self, env):
        if env is not None:
            if type(env)==dict:
                self.env = env

    def set_cwd(self, cwd):
        self.cwd = cwd

    def add_python_buffer_env(self):
        if "PYTHONUNBUFFERED" not in self.env:
            self.env["PYTHONUNBUFFERED"] = "1"

    def check_realtime_output(self):
        while self.running:
            output = self.process.stdout.readline()
            if output:
                out = output.strip().decode('utf-8')
                self.analyse_signal(out)
            if self.process.poll() is not None:
                self.running = False
                self.communicate_thread.send_signal([self.process_id, 'status', 'Done'])
                break

    def analyse_missed_stdout(self):
        stdout, stderr = self.process.communicate()
        print(stdout)
        print(stderr)
        out = stdout.strip().decode('utf-8')
        self.buffer_stdout(out)


    def buffer_stdout(self, out):

        buffered_stdout = ''
        last_percent = None
        last_task = None
        last_stdout_line = None

        for line in out.split('\n'):
            if 'wizard_task_percent:' in line:
                try:
                    last_percent = round(float(line.split(':')[-1]), 0)
                except:
                    self.communicate_thread.send_signal([self.process_id, 'stdout', str(traceback.format_exc())])
            elif 'wizard_task_name:' in line:
                last_task = line.split(':')[-1]
            else:
                buffered_stdout += line+'\n'
                last_stdout_line = line

        self.out += buffered_stdout

        if last_percent is not None:
            self.communicate_thread.send_percent([self.process_id, 'percent', last_percent])
        if last_task is not None:
            self.communicate_thread.send_signal([self.process_id, 'current_task', last_task])

        if self.print_stdout:
            print(buffered_stdout)

    def set_done(self):
        if self.running == True:
            if self.process is not None:
                self.process.kill()
            self.running = False

    def analyse_signal(self, out):
        if 'wizard_task_percent:' in out:
            try:
                percent = round(float(out.split(':')[-1]), 0)
                self.communicate_thread.send_percent([self.process_id, 'percent', percent])
            except:
                logger.error(str(traceback.format_exc()))
        elif 'wizard_task_name:' in out:
            task = out.split(':')[-1]
            self.communicate_thread.send_signal([self.process_id, 'current_task', task])
        elif 'wizard_task_status:' in out:
            status = out.split(':')[-1]
            if status == 'done':
                self.communicate_thread.send_signal([self.process_id, 'status', 'Done'])
                self.set_done()
        else:
            self.out+='\n'+out
            if self.print_stdout:
                print(out)

    def write(self, stdin):
        try:
            stdin = (stdin+'\n').encode('utf-8')
            self.process.stdin.write(stdin)
            self.process.stdin.flush()
        except:
            logger.error(str(traceback.format_exc()))

    def kill(self):
        if self.running == True:
            if self.process is not None:
                self.process.kill()
                self.communicate_thread.send_signal([self.process_id, 'status', 'Killed'])
            self.running = False

    def write_log(self):
        log_name = f"subtask_{self.process_id}.log"
        log_file = path_utils.join(user_vars._subtasks_logs_, log_name)
        tools.create_folder_if_not_exist(user_vars._subtasks_logs_)
        with open(log_file, 'w') as f:
            f.write(self.out)
        self.communicate_thread.send_signal([self.process_id, 'log_file', log_file])

    def build_pycmd(self):
        if self.pycmd is not None:
            if self.pycmd.endswith('.py') and path_utils.isfile(self.pycmd):
                py_file = self.pycmd
            else:
                py_file = tools.temp_file_from_pycmd(self.pycmd)
                
            if sys.argv[0].endswith('.py'):
                self.command = f'python PyWizard.py "{py_file}"'
            else:
                self.command = f'PyWizard "{py_file}"'

    def run(self):
        try:
            self.running = True

            self.communicate_thread = communicate_thread(self)
            self.communicate_thread.start()

            self.communicate_thread.send_signal([self.process_id, 'status', 'Running'])
            self.add_python_buffer_env()

            self.build_pycmd()

            self.process = subprocess.Popen(args = shlex.split(self.command), env=self.env, cwd=self.cwd,
                                            stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.PIPE)

            self.check_realtime_output()
            self.analyse_missed_stdout()
            self.running = False
            self.write_log()
            self.communicate_thread.send_signal([self.process_id, 'end', 1])
            self.communicate_thread.stop()
        except:
            logger.error(str(traceback.format_exc()))

def send_signal(signal_list):
    socket_utils.send_bottle(_DNS_, signal_list, 0.001)

class communicate_thread(Thread):
    def __init__(self, parent = None):
        super(communicate_thread, self).__init__()
        self.parent = parent
        self.percent = 0
        self.running = True
        self.conn = socket_utils.get_connection(_DNS_)
        if self.conn is not None:
            socket_utils.send_signal_with_conn(self.conn, self.parent.process_id)

    def stop(self):
        self.running = False

    def run(self):
        while self.conn is not None and self.running is True:
            raw_data = socket_utils.recvall(self.conn)
            if raw_data is not None:
                try:
                    data = json.loads(raw_data)
                    self.analyse_signal(data)
                except json.decoder.JSONDecodeError:
                    logger.debug("cannot read json data")

    def analyse_signal(self, data):
        if data == 'kill':
            self.parent.kill()
        elif data == 'end':
            self.stop()

    def send_percent(self, signal_list):
        percent = signal_list[-1]
        if percent != self.percent:
            if percent >= self.percent+5 or int(percent) == 100:
                self.send_signal(signal_list)
                self.percent = percent

    def send_signal(self, signal_list):
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, signal_list, only_debug=False):
                self.conn.close()
                self.conn = None
                self.stop()
