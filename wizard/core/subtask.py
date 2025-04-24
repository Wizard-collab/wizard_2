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

"""
This module defines a `subtask` class and related utilities for managing and monitoring
subprocess tasks in a multithreaded environment. It provides functionality to execute
commands or Python scripts in separate threads, capture their output, and communicate
progress and status updates in real-time.

Classes:
    - subtask: Represents a subprocess task executed in a separate thread.
    - communicate_thread: Handles communication with a server using sockets.
    - tasks_server: Manages tasks and handles communication with clients over a socket connection.
    - task_thread: Manages a task's communication and lifecycle using a socket connection.

Functions:
    - send_signal: Sends a signal to the subtasks server using a socket connection.
    - remove_task_from_subtasks_datas_file: Removes a task from the subtasks data file based on the given task ID.

Dependencies:
    - Python modules: threading, subprocess, time, psutil, json, shlex, os, traceback, sys, logging, uuid, yaml
    - Wizard modules: user_vars, environment, tools, path_utils, socket_utils
"""

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
import yaml

# Wizard modules
from wizard.vars import user_vars
from wizard.core import environment
from wizard.core import tools
from wizard.core import path_utils
from wizard.core import socket_utils

logger = logging.getLogger(__name__)


class subtask(Thread):
    """
    A class that represents a subtask executed in a separate thread. This class is designed to manage
    and monitor the execution of a command or Python script, capturing its output and status in real-time.
    Attributes:
        process_id (str): A unique identifier for the subtask process.
        process (subprocess.Popen): The subprocess object representing the running command.
        command (str): The command to be executed.
        task_time (float): The total execution time of the subtask.
        status (str): The current status of the subtask (e.g., 'Running', 'Done', 'Killed').
        creation_time (float): The timestamp when the subtask was created.
        current_task (str): The name of the current task being executed.
        percent (float): The progress percentage of the subtask.
        pycmd (str): The Python command or script to be executed.
        env (dict): The environment variables for the subprocess.
        cwd (str): The working directory for the subprocess.
        print_stdout (bool): Whether to print the subprocess's stdout to the console.
        stream_stdout_buffer (str): A buffer for storing real-time stdout output.
        stream_stdout_last_send (float): The timestamp of the last stdout signal sent.
        running (bool): Whether the subtask is currently running.
        out (str): The accumulated output of the subprocess.
    Methods:
        set_print_stdout(): Enables printing of the subprocess's stdout to the console.
        set_command(command): Sets the command to be executed.
        set_pycmd(pycmd): Sets the Python command or script to be executed.
        set_env(env): Sets the environment variables for the subprocess.
        set_cwd(cwd): Sets the working directory for the subprocess.
        add_python_buffer_env(): Adds the PYTHONUNBUFFERED environment variable if not already set.
        check_realtime_output(): Monitors and processes the real-time output of the subprocess.
        analyse_missed_stdout(): Processes any remaining stdout after the subprocess completes.
        buffer_stdout(out): Buffers and processes the stdout output, extracting progress and task information.
        set_done(): Marks the subtask as done and terminates the subprocess if still running.
        analyse_signal(out): Analyzes a single line of output for progress, task, or status updates.
        write(stdin): Writes input to the subprocess's stdin.
        kill(): Terminates the subprocess and its child processes.
        write_log(): Writes the subtask's output and metadata to a log file.
        build_pycmd(): Constructs the command to execute a Python script with the appropriate arguments.
        run(): Executes the subtask, monitors its progress, and handles its lifecycle.
    """

    def __init__(self, cmd=None, pycmd=None, env=None, cwd=None, print_stdout=False):
        """
        Initializes a new instance of the subtask class.

        Args:
            cmd (str, optional): The command to be executed. Defaults to None.
            pycmd (str, optional): A Python-specific command to be executed. Defaults to None.
            env (dict, optional): The environment variables for the subprocess. Defaults to the current environment.
            cwd (str, optional): The working directory for the subprocess. Defaults to None.
            print_stdout (bool, optional): Whether to print the subprocess's standard output. Defaults to False.

        Attributes:
            process_id (str): A unique identifier for the process.
            process (subprocess.Popen, optional): The subprocess instance. Defaults to None.
            command (str): The command to be executed.
            task_time (float): The time taken by the task. Defaults to 0.
            status (str): The current status of the task. Defaults to 'Running'.
            creation_time (float): The timestamp when the task was created.
            current_task (str): The description of the current task. Defaults to an empty string.
            percent (int): The percentage of task completion. Defaults to 0.
            pycmd (str): A Python-specific command to be executed.
            env (dict): The environment variables for the subprocess.
            cwd (str): The working directory for the subprocess.
            print_stdout (bool): Whether to print the subprocess's standard output.
            stream_stdout_buffer (str): Buffer for the subprocess's standard output stream.
            stream_stdout_last_send (float): Timestamp of the last standard output stream send.
            running (bool): Whether the task is currently running. Defaults to False.
            out (str): The output of the subprocess. Defaults to an empty string.
        """
        super(subtask, self).__init__()
        self.process_id = str(uuid.uuid4())
        self.process = None
        self.command = cmd
        self.task_time = 0
        self.status = 'Running'
        self.creation_time = time.time()
        self.current_task = ''
        self.percent = 0
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
        """
        Enables printing to standard output by setting the `print_stdout` attribute to True.
        """
        self.print_stdout = True

    def set_command(self, command):
        """
        Sets the command attribute for the instance.

        Args:
            command (str): The command to be set.
        """
        self.command = command

    def set_pycmd(self, pycmd):
        """
        Sets the Python command for the current instance.

        Args:
            pycmd (str): The Python command to be set.
        """
        self.pycmd = pycmd

    def set_env(self, env):
        """
        Sets the environment for the current instance.

        Args:
            env (dict): A dictionary containing environment variables to set. 
                        If None or not a dictionary, the method will return without making changes.

        Returns:
            None
        """
        if env is None:
            return
        if type(env) != dict:
            return
        self.env = env

    def set_cwd(self, cwd):
        """
        Sets the current working directory (cwd) for the instance.

        Args:
            cwd (str): The path to set as the current working directory.
        """
        self.cwd = cwd

    def add_python_buffer_env(self):
        """
        Ensures that the environment variable 'PYTHONUNBUFFERED' is set to '1'.

        This function checks if the 'PYTHONUNBUFFERED' variable is already present
        in the `self.env` dictionary. If it is not present, it adds the variable
        with a value of '1'. Setting 'PYTHONUNBUFFERED' to '1' forces Python to
        run in unbuffered mode, which can be useful for real-time output in
        certain scenarios, such as logging or debugging.

        Returns:
            None
        """
        if "PYTHONUNBUFFERED" in self.env:
            return
        self.env["PYTHONUNBUFFERED"] = "1"

    def check_realtime_output(self):
        """
        Monitors the real-time output of a subprocess and processes each line of output.

        This function continuously reads lines from the standard output of a running subprocess
        while the `self.running` flag is True. Each line of output is stripped of whitespace and
        decoded to UTF-8. If decoding fails, the raw string representation of the output is used.
        The processed output is then passed to the `self.analyse_signal` method for further handling.

        If the subprocess terminates (detected via `self.process.poll()`), the function sets
        `self.running` to False, sends a "Done" status signal using `self.communicate_thread.send_signal`,
        and calls `self.set_done()` to perform any necessary cleanup.

        Note:
            - This function assumes `self.process` is a subprocess object with a readable `stdout`.
            - The `self.running` flag controls the loop execution.
            - The `self.analyse_signal` method is expected to handle the processed output.
            - The `self.communicate_thread.send_signal` method is used to send status updates.

        Raises:
            UnicodeDecodeError: If the output cannot be decoded to UTF-8 and no fallback is provided.

        """
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
                self.communicate_thread.send_signal(
                    [self.process_id, 'status', 'Done'])
                self.set_done()
                break

    def analyse_missed_stdout(self):
        """
        Analyzes the standard output (stdout) of a process to handle any missed output.

        This method retrieves the stdout and stderr streams from the process, decodes
        the stdout from bytes to a UTF-8 string, and removes any leading or trailing
        whitespace. The processed stdout is then passed to the `buffer_stdout` method
        for further handling.

        Returns:
            None
        """
        stdout, stderr = self.process.communicate()
        out = stdout.strip().decode('utf-8')
        self.buffer_stdout(out)

    def buffer_stdout(self, out):
        """
        Processes and buffers the standard output stream, extracting specific task-related
        information and sending updates via communication threads.
        Args:
            out (str): The standard output stream as a string, containing lines of text.
        Functionality:
            - Parses the output stream line by line.
            - Extracts task progress percentage from lines containing 'wizard_task_percent:'.
            - Extracts task name from lines containing 'wizard_task_name:'.
            - Buffers other lines of output and appends them to the instance's output buffer.
            - Sends updates to a communication thread for:
                - Standard output updates.
                - Task progress percentage.
                - Current task name.
            - Optionally prints the buffered output if `self.print_stdout` is enabled.
        Raises:
            - Logs and sends traceback information to the communication thread if an error
              occurs while parsing the task progress percentage.
        """

        buffered_stdout = ''
        last_percent = None
        last_task = None
        last_stdout_line = None

        for line in out.split('\n'):
            if 'wizard_task_percent:' in line:
                try:
                    last_percent = round(float(line.split(':')[-1]), 0)
                except:
                    self.communicate_thread.send_signal(
                        [self.process_id, 'stdout', str(traceback.format_exc())])
            elif 'wizard_task_name:' in line:
                last_task = line.split(':')[-1]
            else:
                buffered_stdout += line+'\n'
                last_stdout_line = line

        self.out += buffered_stdout
        self.communicate_thread.send_signal(
            [self.process_id, 'stdout', self.stream_stdout_buffer+buffered_stdout])

        if last_percent is not None:
            self.communicate_thread.send_percent(
                [self.process_id, 'percent', last_percent])
        if last_task is not None:
            self.communicate_thread.send_signal(
                [self.process_id, 'current_task', last_task])

        if self.print_stdout:
            print(buffered_stdout)

    def set_done(self):
        """
        Marks the current task as done by updating its status and stopping any associated process.

        This method performs the following actions:
        1. Sets the task's status to 'Done'.
        2. Checks if the task is currently running. If not, it exits early.
        3. If a process is associated with the task, it terminates the process.
        4. Updates the running state to False after stopping the process.

        Returns:
            None
        """
        self.status = 'Done'
        if self.running != True:
            return
        if self.process is None:
            return
        self.process.kill()
        self.running = False

    def analyse_signal(self, out):
        """
        Analyzes the output signal and performs actions based on its content.

        Args:
            out (str): The output signal string to be analyzed.

        Behavior:
            - If the signal contains 'wizard_task_percent:', extracts the percentage value,
              sends it to the communication thread, and updates the `percent` attribute.
            - If the signal contains 'wizard_task_name:', extracts the task name,
              sends it to the communication thread, and updates the `current_task` attribute.
            - If the signal contains 'wizard_task_status:', checks the status value.
              If the status is 'done', sends a 'Done' status signal, updates the `status`
              attribute, and marks the task as done.
            - For any other signal, appends it to the output buffer, optionally prints it,
              and sends the buffered output to the communication thread if a certain time
              interval has passed.

        Exceptions:
            - Logs any exceptions that occur during the processing of percentage values.

        Attributes Updated:
            - `percent`: Updated with the extracted percentage value.
            - `current_task`: Updated with the extracted task name.
            - `status`: Updated to 'Done' if the status signal indicates completion.
            - `out`: Appended with unrecognized signal content.
            - `stream_stdout_buffer`: Appended with unrecognized signal content and sent
              periodically to the communication thread.
        """
        if 'wizard_task_percent:' in out:
            try:
                percent = round(float(out.split(':')[-1]), 0)
                self.communicate_thread.send_percent(
                    [self.process_id, 'percent', percent])
                self.percent = percent
            except:
                logger.error(str(traceback.format_exc()))
        elif 'wizard_task_name:' in out:
            task = out.split(':')[-1]
            self.communicate_thread.send_signal(
                [self.process_id, 'current_task', task])
            self.current_task = task
        elif 'wizard_task_status:' in out:
            status = out.split(':')[-1]
            if status == 'done':
                self.communicate_thread.send_signal(
                    [self.process_id, 'status', 'Done'])
                self.status = 'Done'
                self.set_done()
        else:
            self.out += '\n'+out
            self.stream_stdout_buffer += '\n'+out
            if self.print_stdout:
                print(out)
            if time.time() - self.stream_stdout_last_send > 0.2:
                self.communicate_thread.send_signal(
                    [self.process_id, 'stdout', self.stream_stdout_buffer])
                self.stream_stdout_buffer = ''
                self.stream_stdout_last_send = time.time()

    def write(self, stdin):
        """
        Writes the given input to the standard input (stdin) of a subprocess.

        Args:
            stdin (str): The input string to be written to the subprocess's stdin.

        Raises:
            Logs an error if an exception occurs during the write or flush operation.
        """
        try:
            stdin = (stdin+'\n').encode('utf-8')
            self.process.stdin.write(stdin)
            self.process.stdin.flush()
        except:
            logger.error(str(traceback.format_exc()))

    def kill(self):
        """
        Terminates the process and its child processes associated with this instance.

        This method checks if the process is running and, if so, terminates all child
        processes recursively before killing the main process. It also updates the
        status and running state of the instance and sends a signal indicating that
        the process has been killed.

        Returns:
            None
        """
        if self.running != True:
            return
        if self.process is None:
            return
        for child in psutil.Process(self.process.pid).children(recursive=True):
            child.kill()
        self.process.kill()
        self.communicate_thread.send_signal(
            [self.process_id, 'status', 'Killed'])
        self.status = 'Killed'
        self.running = False

    def write_log(self):
        """
        Writes the log data for the current subtask to a log file and updates the 
        subtask data YAML file with relevant metadata.
        This function performs the following steps:
        1. Creates a log file named `subtask_<process_id>.log` in the specified 
           subtasks logs directory.
        2. Writes the output (`self.out`) of the subtask to the log file.
        3. Reads or initializes a dictionary from the subtasks data YAML file.
        4. Updates the dictionary with metadata about the current subtask, including:
           - Project name
           - Task time
           - Status
           - Creation time
           - Current task
           - Percent completion
           - Log file path
        5. Writes the updated dictionary back to the subtasks data YAML file.
        6. Sends a signal with the process ID and log file path to the communication thread.
        Attributes:
            self.process_id (str): Unique identifier for the subtask process.
            self.out (str): Output data to be written to the log file.
            self.task_time (str): Time taken for the task.
            self.status (str): Current status of the subtask.
            self.creation_time (str): Timestamp of subtask creation.
            self.current_task (str): Description of the current task.
            self.percent (float): Percentage of task completion.
            self.communicate_thread (object): Thread object used for communication.
        Raises:
            IOError: If there are issues reading or writing to the log or YAML files.
        """
        log_name = f"subtask_{self.process_id}.log"
        log_file = path_utils.join(user_vars._subtasks_logs_, log_name)
        subtasks_datas_file = path_utils.join(
            user_vars._subtasks_logs_, user_vars._subtasks_datas_yaml_)
        tools.create_folder_if_not_exist(user_vars._subtasks_logs_)
        with open(log_file, 'w') as f:
            f.write(self.out)
        if path_utils.isfile(subtasks_datas_file):
            with open(subtasks_datas_file, 'r') as f:
                datas_dic = yaml.load(f, Loader=yaml.Loader)
        else:
            datas_dic = dict()
        datas_dic[self.process_id] = dict()
        datas_dic[self.process_id]['project'] = environment.get_project_name()
        datas_dic[self.process_id]['time'] = self.task_time
        datas_dic[self.process_id]['status'] = self.status
        datas_dic[self.process_id]['creation_time'] = self.creation_time
        datas_dic[self.process_id]['current_task'] = self.current_task
        datas_dic[self.process_id]['percent'] = self.percent
        datas_dic[self.process_id]['log_file'] = log_file
        with open(subtasks_datas_file, 'w') as f:
            yaml.dump(datas_dic, f)

        self.communicate_thread.send_signal(
            [self.process_id, 'log_file', log_file])

    def build_pycmd(self):
        """
        Constructs a command string to execute a Python script with specific parameters.
        This method builds a command string (`self.command`) that includes various
        environment-specific parameters and the path to a Python script. The command
        is intended to be executed by the `wizard_cmd` tool or its Python equivalent.
        Returns:
            None
        Behavior:
            - If `self.pycmd` is `None`, the method returns without doing anything.
            - If `self.pycmd` ends with `.py` and is a valid file, it is used as the
              Python script to execute.
            - Otherwise, a temporary file is created from `self.pycmd` using
              `tools.temp_file_from_pycmd`.
            - The method determines the appropriate executable (`python wizard_cmd.py`
              or `wizard_cmd`) based on the current script's filename.
            - Environment-specific parameters such as PostgreSQL DNS, repository name,
              user name, project name, and team DNS are retrieved and included in the
              command string.
            - The constructed command string is stored in `self.command`.
        Attributes:
            self.pycmd (str): The Python command or script path to be executed.
            self.command (str): The constructed command string to execute the script.
        Dependencies:
            - `path_utils.isfile`: Checks if a file exists.
            - `tools.temp_file_from_pycmd`: Creates a temporary file from a Python command.
            - `environment.get_psql_dns`: Retrieves the PostgreSQL DNS.
            - `environment.get_repository`: Retrieves the repository name.
            - `environment.get_user`: Retrieves the current user name.
            - `environment.get_project_name`: Retrieves the project name.
            - `environment.get_team_dns`: Retrieves the team DNS as a dictionary.
            - `json.dumps`: Converts the team DNS dictionary to a JSON string.
            - `sys.argv[0]`: Used to determine the current script's filename.
        """
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
        """
        Executes the main logic of the subtask, managing its lifecycle and handling subprocess execution.
        This method performs the following steps:
        1. Records the start time for task execution.
        2. Sets the `running` flag to True to indicate the task is active.
        3. Initializes and starts a communication thread for inter-process communication.
        4. Configures the Python environment variables for the subprocess.
        5. Builds the command to be executed by the subprocess.
        6. Starts the subprocess using the constructed command and environment settings.
        7. Sends a signal to indicate the task's running status.
        8. Monitors the real-time output of the subprocess.
        9. Analyzes any missed standard output from the subprocess.
        10. Calculates the total execution time of the task.
        11. Sets the `running` flag to False to indicate the task has completed.
        12. Writes execution logs.
        13. Sends a signal to indicate the task's completion status.
        14. Stops the communication thread.
        If an exception occurs during execution, it logs the error traceback.
        Raises:
            Exception: Logs any exception that occurs during the execution process.
        """
        try:
            start_time = time.perf_counter()
            self.running = True

            self.communicate_thread = communicate_thread(self)
            self.communicate_thread.start()

            self.add_python_buffer_env()

            self.build_pycmd()

            self.process = subprocess.Popen(args=shlex.split(self.command), env=self.env, cwd=self.cwd,
                                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.PIPE)

            self.communicate_thread.send_signal(
                [self.process_id, 'status', 'Running'])

            self.check_realtime_output()
            self.analyse_missed_stdout()
            self.task_time = time.perf_counter()-start_time
            self.running = False
            self.write_log()
            self.communicate_thread.send_signal([self.process_id, 'end', 1])
            self.communicate_thread.stop()

        except:
            logger.error(str(traceback.format_exc()))


def send_signal(signal_list):
    """
    Sends a signal to the subtasks server using a socket connection.

    Args:
        signal_list (list): A list of signals to be sent to the server.

    Notes:
        - The server address is set to 'localhost'.
        - The port is dynamically retrieved from the environment configuration.
        - A timeout of 0.001 seconds is used for the socket communication.
    """
    socket_utils.send_bottle(
        ('localhost', environment.get_subtasks_server_port()), signal_list, 0.001)


class communicate_thread(Thread):
    """
    A thread class for handling communication with a server using sockets. This class is responsible
    for sending and receiving signals, analyzing received data, and managing the thread's lifecycle.
    Attributes:
        parent (object): The parent object that owns this thread instance.
        percent (int): The current progress percentage being tracked.
        running (bool): A flag indicating whether the thread is running.
        conn (socket): The socket connection used for communication.
    Methods:
        __init__(parent=None):
            Initializes the thread, establishes a socket connection, and sends the parent process ID.
        stop():
            Stops the thread by setting the running flag to False.
        run():
            The main loop of the thread that listens for incoming data from the socket connection
            and processes it.
        analyse_signal(data):
            Analyzes the received signal data and performs actions based on the signal type.
        send_percent(signal_list):
            Sends progress percentage updates if the percentage has changed significantly.
        send_signal(signal_list):
            Sends a signal to the server through the socket connection.
    """

    def __init__(self, parent=None):
        """
        Initializes the communicate_thread instance.

        Args:
            parent (object, optional): The parent object that owns this thread instance. Defaults to None.

        Attributes:
            parent (object): The parent object passed during initialization.
            percent (int): Tracks the current progress percentage. Defaults to 0.
            running (bool): Indicates whether the thread is running. Defaults to True.
            conn (socket): The socket connection used for communication. If the connection
                           is successfully established, it sends the parent process ID to the server.
        """
        super(communicate_thread, self).__init__()
        self.parent = parent
        self.percent = 0
        self.running = True
        self.conn = socket_utils.get_connection(
            ('localhost', environment.get_subtasks_server_port()))
        if self.conn is not None:
            socket_utils.send_signal_with_conn(
                self.conn, self.parent.process_id)

    def stop(self):
        """
        Stops the execution of the current task by setting the running flag to False.
        """
        self.running = False

    def run(self):
        """
        Continuously receives data from a socket connection, processes it as JSON, 
        and analyzes the resulting data.

        This method runs in a loop as long as the `conn` attribute is not None 
        and the `running` attribute is True. It receives raw data from the socket 
        connection, attempts to decode it as JSON, and passes the decoded data 
        to the `analyse_signal` method for further processing. If the JSON decoding 
        fails, it logs a debug message.

        Raises:
            json.decoder.JSONDecodeError: If the received data cannot be decoded as JSON.

        Note:
            - The loop will terminate if `conn` becomes None or `running` is set to False.
            - Ensure that `self.conn` is a valid socket connection and `self.running` 
              is properly managed to avoid infinite loops.
        """
        while self.conn is not None and self.running is True:
            raw_data = socket_utils.recvall(self.conn)
            if raw_data is not None:
                try:
                    data = json.loads(raw_data)
                    self.analyse_signal(data)
                except json.decoder.JSONDecodeError:
                    logger.debug("cannot read json data")

    def analyse_signal(self, data):
        """
        Analyzes the provided signal data and performs the corresponding action.

        Args:
            data (str): The signal data to analyze. Expected values are:
                - 'kill': Triggers the parent object's `kill` method.
                - 'end': Stops the current process by calling the `stop` method.

        Raises:
            None
        """
        if data == 'kill':
            self.parent.kill()
        elif data == 'end':
            self.stop()

    def send_percent(self, signal_list):
        """
        Updates and sends the progress percentage signal if certain conditions are met.

        Args:
            signal_list (list): A list of signals where the last element represents the current progress percentage.

        Behavior:
            - If the current percentage (`percent`) is the same as the stored percentage (`self.percent`), the function does nothing.
            - If the current percentage is at least 5% greater than the stored percentage or equals 100%, 
              the function sends the signal using `self.send_signal(signal_list)` and updates `self.percent`.
        """
        percent = signal_list[-1]
        if percent == self.percent:
            return
        if percent >= self.percent+5 or int(percent) == 100:
            self.send_signal(signal_list)
            self.percent = percent

    def send_signal(self, signal_list):
        """
        Sends a signal using the established connection.

        Args:
            signal_list (list): A list of signals to be sent.

        Returns:
            None

        Behavior:
            - If the connection (`self.conn`) is `None`, the method returns immediately.
            - Attempts to send the signal list using the `socket_utils.send_signal_with_conn` function.
            - If sending the signal fails:
                - Closes the connection.
                - Sets `self.conn` to `None`.
                - Stops the current process by calling `self.stop()`.
        """
        if self.conn is None:
            return
        if not socket_utils.send_signal_with_conn(self.conn, signal_list, only_debug=False):
            self.conn.close()
            self.conn = None
            self.stop()


class tasks_server(Thread):
    """
    A server class that manages tasks and handles communication with clients 
    over a socket connection. This class runs in a separate thread and listens 
    for incoming connections to process task-related signals.
    Attributes:
        port (int): The port number on which the server listens for connections.
        server (socket.socket): The server socket object.
        server_address (str): The address of the server.
        running (bool): A flag indicating whether the server is running.
        threads (dict): A dictionary mapping process IDs to their respective 
                        socket connections.
    Methods:
        run():
            Starts the server loop to accept and process incoming connections.
        new_thread(process_id, conn):
            Creates and starts a new thread to handle a specific task.
        stop():
            Stops the server and closes the socket connection.
    """

    def __init__(self):
        """
        Initializes an instance of the tasks_server class.

        This constructor sets up the server for handling subtasks by:
        - Initializing the parent class using `super()`.
        - Assigning a port for the server using `socket_utils.get_port`.
        - Setting the port in the environment using `environment.set_subtasks_server_port`.
        - Creating a server and its address using `socket_utils.get_server`.
        - Initializing a flag `running` to indicate the server's running state.
        - Initializing a dictionary `threads` to manage server threads.
        """
        super(tasks_server, self).__init__()
        self.port = socket_utils.get_port('localhost')
        environment.set_subtasks_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(
            ('localhost', self.port))
        self.running = True
        self.threads = dict()

    def run(self):
        """
        Continuously listens for incoming connections and processes signals.

        This method runs in a loop while the `running` attribute is True. It accepts
        incoming connections from a server socket, verifies the address of the
        connection, and processes incoming signals. If a valid signal is received,
        it spawns a new thread to handle the associated process.

        Exceptions:
            - OSError: Ignored silently, allowing the loop to continue.
            - Any other exception: Logged as an error with a traceback.

        Note:
            - The method relies on `socket_utils.recvall` to receive data from the connection.
            - The `new_thread` method is called to handle the process in a separate thread.
        """
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
        """
        Creates and starts a new thread for a specific process and stores the connection.

        Args:
            process_id (int): The unique identifier for the process.
            conn (object): The connection object associated with the process.

        Side Effects:
            - Initializes and starts a new thread using the `task_thread` class.
            - Stores the connection object in the `threads` dictionary with the process ID as the key.
        """
        self.task_thread = task_thread(conn, process_id)
        self.task_thread.start()
        self.threads[process_id] = conn

    def stop(self):
        """
        Stops the server and updates the running status.

        This method closes the server connection and sets the `running` attribute
        to `False`, effectively stopping the server's operation.
        """
        self.server.close()
        self.running = False


class task_thread(Thread):
    """
    A thread class for managing a task's communication and lifecycle using a socket connection.
    Attributes:
        conn (socket): The socket connection used for communication.
        process_id (int): The unique identifier for the task.
        running (bool): A flag indicating whether the thread is running.
    Methods:
        run():
            Continuously listens for incoming data on the socket connection and processes it.
        kill():
            Sends a 'kill' signal to the connected process and closes the connection if necessary.
        get_stdout():
            Sends a 'get_stdout' signal to the connected process and closes the connection if necessary.
        stop():
            Stops the thread by setting the running flag to False and closing the connection.
        analyse_signal(raw_data):
            Processes incoming data from the socket connection and handles various signal types.
    """

    def __init__(self, conn, process_id):
        """
        Initializes a new instance of the task_thread class.

        Args:
            conn: The connection object used for communication or data transfer.
            process_id: The identifier for the process associated with this thread.

        Attributes:
            conn: Stores the provided connection object.
            process_id: Stores the provided process identifier.
            running (bool): Indicates whether the thread is currently running. Defaults to True.
        """
        super(task_thread, self).__init__()
        self.conn = conn
        self.process_id = process_id
        self.running = True

    def run(self):
        """
        Executes the main loop for processing incoming data from a connection.

        This method continuously receives data from a socket connection while the
        `running` flag is True and the `conn` attribute is not None. It processes
        the received data using the `analyse_signal` method. If no data is received,
        it closes the connection. Any exceptions encountered during execution are
        logged.

        Raises:
            Exception: Logs any exception that occurs during the execution of the loop.
        """
        while self.running and self.conn is not None:
            try:
                raw_data = socket_utils.recvall(self.conn)
                if raw_data is not None:
                    self.analyse_signal(raw_data)
                else:
                    if self.conn is not None:
                        self.conn.close()
                        self.conn = None
                        # self.connection_dead.emit(1)
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def kill(self):
        """
        Terminates the connection associated with this instance.

        This method attempts to send a 'kill' signal through the existing connection.
        If the signal cannot be sent, it ensures the connection is properly closed
        and set to None to release resources.

        Note:
            The `self.conn` attribute represents the connection object. If it is
            already None, no action is taken.
        """
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, 'kill'):
                if self.conn is not None:
                    self.conn.close()
                    self.conn = None
                    # self.connection_dead.emit(1)

    def get_stdout(self):
        """
        Sends a 'get_stdout' signal to the connected process to request its standard output.

        This method attempts to send a 'get_stdout' signal through the existing connection.
        If the signal cannot be sent, it ensures the connection is properly closed and set
        to None to release resources.

        Behavior:
            - If the connection (`self.conn`) is not None, it sends the 'get_stdout' signal.
            - If sending the signal fails, the connection is closed and set to None.

        Note:
            The `self.conn` attribute represents the connection object. If it is already None,
            no action is taken.
        """
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, 'get_stdout'):
                if self.conn is not None:
                    self.conn.close()
                    self.conn = None
                    # self.connection_dead.emit(1)

    def stop(self):
        """
        Stops the current task by setting the running flag to False and closing the connection if it exists.

        This method ensures that the task is properly terminated by:
        - Setting the `running` attribute to False to indicate the task is no longer active.
        - Closing the connection (`conn`) if it is not None, and setting it to None afterward.

        Note:
        - The `self.connection_dead.emit(1)` line is commented out and not currently in use.
        """
        self.running = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None
            # self.connection_dead.emit(1)

    def analyse_signal(self, raw_data):
        """
        Analyzes a signal represented as a JSON-encoded string and performs actions
        based on the type of data contained in the signal.
        Args:
            raw_data (str): A JSON-encoded string containing the signal data. The
                            expected format is a list where:
                            - The second element specifies the data type.
                            - The third element contains the associated data.
        Behavior:
            - If the data type is 'percent', logs the progress percentage.
            - If the data type is 'current_task', logs the current task description.
            - If the data type is 'status', logs the status message.
            - If the data type is 'log_file', logs the path to the log file.
            - If the data type is 'end', logs a stopped message and stops the task.
            - If the data type is 'stdout', no action is taken.
            - If the JSON decoding fails, logs a debug message indicating the failure.
        Raises:
            None
        """
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


def remove_task_from_subtasks_datas_file(task_id):
    """
    Removes a task from the subtasks data file based on the given task ID.

    This function checks if the subtasks data file exists. If it does, it loads
    the file as a dictionary, removes the entry corresponding to the provided
    task ID (if it exists), and writes the updated dictionary back to the file.

    Args:
        task_id (str): The unique identifier of the task to be removed.

    Returns:
        int: Returns 1 if the task was successfully removed.
        None: Returns None if the file does not exist, the task ID is not found,
              or no changes were made.
    """
    subtasks_datas_file = path_utils.join(
        user_vars._subtasks_logs_, user_vars._subtasks_datas_yaml_)
    if not path_utils.isfile(subtasks_datas_file):
        return
    with open(subtasks_datas_file, 'r') as f:
        datas_dic = yaml.load(f, Loader=yaml.Loader)
    if task_id not in datas_dic.keys():
        return
    del datas_dic[task_id]
    with open(subtasks_datas_file, 'w') as f:
        yaml.dump(datas_dic, f)
    return 1
