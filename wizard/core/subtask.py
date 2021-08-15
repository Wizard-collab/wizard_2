# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module manage substasks

# Python modules
from PyQt5.QtCore import QThread, pyqtSignal
import subprocess
import time
import shlex
import os
import traceback

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

class subtask_thread(QThread):

    stdout_signal = pyqtSignal(str)
    status_signal = pyqtSignal(str)
    current_task_signal = pyqtSignal(str)
    time_signal = pyqtSignal(float)
    percent_signal = pyqtSignal(float)
    stats_signal = pyqtSignal(object)

    def __init__(self):
        super(subtask_thread, self).__init__()
        self.process = None
        self.clock_thread = clock_thread()
        self.command = None
        self.env = os.environ.copy()
        self.cwd = None
        self.running = True
        self.connect_functions()

    def connect_functions(self):
        self.clock_thread.time_signal.connect(self.time_signal.emit)

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
                self.status_signal.emit('Done')
                self.running = False
                break
            if output:
                out = output.strip().decode('utf-8')
                self.analyse_signal(out)

    def analyse_signal(self, out):
        if 'wizard_task_percent:' in out:
            percent = float(out.split(':')[-1])
            self.percent_signal.emit(percent)
        elif 'wizard_task_name:' in out:
            task = out.split(':')[-1]
            self.current_task_signal.emit(task)
        else:
            self.stdout_signal.emit(out)

    def kill(self):
        self.clock_thread.stop()
        if self.running == True:
            self.running = False
        if self.process is not None:
            self.process.kill()
            self.status_signal.emit('Killed')

    def run(self):
        try:
            self.running = True
            self.status_signal.emit('Running')
            self.add_python_buffer_env()
            start_time = time.time()
            self.clock_thread.start()
            self.process = subprocess.Popen(args = shlex.split(self.command), env=self.env, cwd=self.cwd,
                                            stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
            self.check_output()
            self.clock_thread.stop()
            process_time = (time.time()-start_time)
            self.time_signal.emit(process_time)
        except:
            self.stdout_signal.emit(str(traceback.format_exc()))

class clock_thread(QThread):

    time_signal = pyqtSignal(object)

    def __init__(self):
        super(clock_thread, self).__init__()
        self.running = True

    def stop(self):
        self.running = False

    def run(self):
        self.running = True
        time_count = 0
        self.time_signal.emit(time_count)
        while self.running:
            time.sleep(1)
            time_count += 1
            self.time_signal.emit(time_count)
