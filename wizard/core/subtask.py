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
import psutil
import json
import shlex
import os
import traceback
import sys
import logging
import uuid

# Wizard modules
from wizard.vars import user_vars
from wizard.core import environment
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import socket_utils

logger = logging.getLogger(__name__)

class subtask(Thread):
    def __init__(self, cmd=None, pycmd=None, env=None, cwd=None, print_stdout=False):
        super(subtask, self).__init__()
        self.process_id = str(uuid.uuid4())
        self.process = None
        self.command = cmd
        self.pycmd = pycmd
        if env is None:
            self.env = os.environ.copy()
        else:
            self.env = env
        self.cwd = cwd
        self.print_stdout = print_stdout
        self.stream_stdout_buffer = ''
        self.stream_stdout_last_send = 0
        self.running = False
        self.out = ''

    def set_print_stdout(self):
        self.print_stdout=True

    def set_command(self, command):
        self.command = command

    def set_pycmd(self, pycmd):
        self.pycmd = pycmd

    def set_env(self, env):
        if env is None:
            return
        if type(env)!=dict:
            return
        self.env = env

    def set_cwd(self, cwd):
        self.cwd = cwd

    def add_python_buffer_env(self):
        if "PYTHONUNBUFFERED" in self.env:
            return
        self.env["PYTHONUNBUFFERED"] = "1"

    def check_realtime_output(self):
        while self.running:
            output = self.process.stdout.readline()
            if output:
                try:
                    out = output.strip().decode('utf-8')
                except UnicodeDecodeError:
                    out = str(output.strip())
                self.analyse_signal(out)
            if self.process.poll() is not None:
                self.running = False
                self.communicate_thread.send_signal([self.process_id, 'status', 'Done'])
                break

    def analyse_missed_stdout(self):
        stdout, stderr = self.process.communicate()
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
        self.communicate_thread.send_signal([self.process_id, 'stdout', self.stream_stdout_buffer+buffered_stdout])

        if last_percent is not None:
            self.communicate_thread.send_percent([self.process_id, 'percent', last_percent])
        if last_task is not None:
            self.communicate_thread.send_signal([self.process_id, 'current_task', last_task])

        if self.print_stdout:
            print(buffered_stdout)

    def set_done(self):
        if self.running != True:
            return
        if self.process is None:
            return
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
            self.stream_stdout_buffer += '\n'+out
            if self.print_stdout:
                print(out)
            if time.time() - self.stream_stdout_last_send > 0.2:
                self.communicate_thread.send_signal([self.process_id, 'stdout', self.stream_stdout_buffer])
                self.stream_stdout_buffer = ''
                self.stream_stdout_last_send = time.time()

    def write(self, stdin):
        try:
            stdin = (stdin+'\n').encode('utf-8')
            self.process.stdin.write(stdin)
            self.process.stdin.flush()
        except:
            logger.error(str(traceback.format_exc()))

    def kill(self):
        if self.running != True:
            return
        if self.process is None:
            return
        for child in psutil.Process(self.process.pid).children(recursive=True):
            child.kill()
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
        if self.pycmd is None:
            return
        if self.pycmd.endswith('.py') and path_utils.isfile(self.pycmd):
            py_file = self.pycmd
        else:
            py_file = tools.temp_file_from_pycmd(self.pycmd)
        
        if sys.argv[0].endswith('.py'):
            executable = 'python wizard_cmd.py'
        else:
            executable = 'wizard_cmd'

        psql_dns = environment.get_psql_dns()
        repository_name = environment.get_repository()[11:]
        user_name = environment.get_user()
        project_name = environment.get_project_name()
        team_dns = json.dumps(environment.get_team_dns())

        self.command = f'{executable} '
        self.command += f'-psqlDns "{psql_dns}" '
        self.command += f'-repository "{repository_name}" '
        self.command += f'-user "{user_name}" '
        self.command += f'-project "{project_name}" '
        self.command += f'-teamDns "{team_dns}" '
        self.command += f'-pyfile "{py_file}"'

    def run(self):
        try:
            self.running = True

            self.communicate_thread = communicate_thread(self)
            self.communicate_thread.start()

            self.add_python_buffer_env()

            self.build_pycmd()

            self.process = subprocess.Popen(args = shlex.split(self.command), env=self.env, cwd=self.cwd,
                                            stdout = subprocess.PIPE, stderr = subprocess.STDOUT, stdin = subprocess.PIPE)

            self.communicate_thread.send_signal([self.process_id, 'status', 'Running'])
            
            self.check_realtime_output()
            self.analyse_missed_stdout()
            self.running = False
            self.write_log()
            self.communicate_thread.send_signal([self.process_id, 'end', 1])
            self.communicate_thread.stop()
        except:
            logger.error(str(traceback.format_exc()))

def send_signal(signal_list):
    socket_utils.send_bottle(('localhost', environment.get_subtasks_server_port()), signal_list, 0.001)

class communicate_thread(Thread):
    def __init__(self, parent = None):
        super(communicate_thread, self).__init__()
        self.parent = parent
        self.percent = 0
        self.running = True
        self.conn = socket_utils.get_connection(('localhost', environment.get_subtasks_server_port()))
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
        if percent == self.percent:
            return
        if percent >= self.percent+5 or int(percent) == 100:
            self.send_signal(signal_list)
            self.percent = percent

    def send_signal(self, signal_list):
        if self.conn is None:
            return
        if not socket_utils.send_signal_with_conn(self.conn, signal_list, only_debug=False):
            self.conn.close()
            self.conn = None
            self.stop()

class tasks_server(Thread):
    def __init__(self):
        super(tasks_server, self).__init__()
        self.port = socket_utils.get_port('localhost')
        environment.set_subtasks_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(('localhost', self.port))
        self.running = True
        self.threads = dict()

    def run(self):
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] == self.server_address:
                    signal_as_str = socket_utils.recvall(conn)
                    if signal_as_str:
                        process_id = json.loads(signal_as_str)
                        self.new_thread(process_id, conn)
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def new_thread(self, process_id, conn):
        self.task_thread = task_thread(conn, process_id)
        self.task_thread.start()
        self.threads[process_id] = conn

    def stop(self):
        self.server.close()
        self.running = False

class task_thread(Thread):
    def __init__(self, conn, process_id):
        super(task_thread, self).__init__()
        self.conn = conn
        self.process_id = process_id
        self.running = True

    def run(self):
        while self.running and self.conn is not None:
            try:
                raw_data = socket_utils.recvall(self.conn)
                if raw_data is not None:
                    self.analyse_signal(raw_data)
                else:
                    if self.conn is not None:
                        self.conn.close()
                        self.conn = None
                        #self.connection_dead.emit(1)
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def kill(self):
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, 'kill'):
                if self.conn is not None:
                    self.conn.close()
                    self.conn = None
                    #self.connection_dead.emit(1)

    def get_stdout(self):
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, 'get_stdout'):
                if self.conn is not None:
                    self.conn.close()
                    self.conn = None
                    #self.connection_dead.emit(1)

    def stop(self):
        self.running = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            #self.connection_dead.emit(1)

    def analyse_signal(self, raw_data):
        try:
            signal_list = json.loads(raw_data)
            data_type = signal_list[1]
            data = signal_list[2]

            if data_type == 'percent':
                print(f"Task id : {self.process_id} | Progress : {data}% ")
            elif data_type == 'current_task':
                print(f"Task id : {self.process_id} | Current task : {data} ")
            elif data_type == 'status':
                print(f"Task id : {self.process_id} | Status : {data} ")
            elif data_type == 'log_file':
                print(f"Task id : {self.process_id} | Log file : {data} ")
            elif data_type == 'end':
                print(f"Task id : {self.process_id} | Stopped ")
                self.stop()
            elif data_type == 'stdout':
                pass
        except json.decoder.JSONDecodeError:
            logger.debug("cannot read json data")