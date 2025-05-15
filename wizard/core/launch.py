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

# The main wizard software launching module
# This module permits to launch a work version ( id )
# It build the command and environment for the Popen
# call

"""
This module serves as the main launching mechanism for the Wizard software. It provides
functions and classes to manage the lifecycle of software processes, including launching,
terminating, and managing work environments. The module is designed to interact with
the Wizard ecosystem, including user management, project data, and environment settings.
Key Features:
- Launch specific work versions of software with appropriate environment configurations.
- Terminate individual or all running software processes.
- Manage software threads in a multi-threaded environment.
- Build commands and environment variables dynamically based on project and software data.
- Communicate with the software server using socket-based signals.
Classes:
- `software_thread`: Manages the execution of a software process in a separate thread.
- `softwares_server`: A server class to manage software threads and handle socket communication.
Functions:
- `launch_work_version(version_id)`: Sends a signal to launch a specific work version.
- `kill(work_env_id)`: Sends a signal to terminate a specific work environment process.
- `kill_all()`: Sends a signal to terminate all processes managed by the software server.
- `died(work_env_id)`: Sends a signal to notify that a specific work environment has terminated.
- `get()`: Sends a signal to retrieve a list of active software threads.
- `core_kill_software_thread(software_thread)`: Terminates a specified software thread.
- `core_launch_version(version_id)`: Launches a specific version of a project in the appropriate software environment.
- `build_command(file_path, software_row, version_id)`: Constructs a command string to launch a software application.
- `build_env(work_env_id, software_row, version_id, mode)`: Configures environment variables for launching a software.
- Python modules: `os`, `subprocess`, `shlex`, `json`, `traceback`, `time`, `threading`, `logging`.
- Wizard modules: `user`, `assets`, `project`, `environment`, `socket_utils`, `path_utils`, `softwares_vars`.
- Wizard GUI modules: `gui_server`.
Usage:
This module is intended to be used as part of the Wizard software suite. It integrates
with other Wizard modules to provide a seamless experience for managing software processes
and work environments.
"""

# Python modules
import os
import subprocess
import shlex
import json
import traceback
import time
from threading import Thread
import logging

# Wizard modules
from wizard.core import user
from wizard.core import assets
from wizard.core import project
from wizard.core import environment
from wizard.core import socket_utils
from wizard.core import path_utils
from wizard.vars import softwares_vars

# Wizard gui modules
from wizard.gui import gui_server

logger = logging.getLogger(__name__)


def launch_work_version(version_id):
    """
    Sends a signal to launch a specific work version on the software server.

    Args:
        version_id (int): The ID of the version to be launched.

    Returns:
        Any: The response from the server after sending the signal.

    Notes:
        - The function constructs a signal dictionary with the function name 
          and version ID, then sends it to the software server using 
          `socket_utils.send_signal`.
        - The server address is assumed to be 'localhost', and the port is 
          retrieved from `environment.get_softwares_server_port()`.
        - A timeout of 0.5 seconds is set for the signal transmission.
    """
    signal_dic = dict()
    signal_dic['function'] = 'launch'
    signal_dic['version_id'] = version_id
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=0.5)


def kill(work_env_id):
    """
    Sends a signal to terminate a specific work environment process.

    Args:
        work_env_id (int): The ID of the work environment to be terminated.

    Returns:
        Any: The response from the server after sending the termination signal.

    Notes:
        - Constructs a signal dictionary with the function name and work 
          environment ID, then sends it to the software server using 
          `socket_utils.send_signal`.
        - The server address is assumed to be 'localhost', and the port is 
          retrieved from `environment.get_softwares_server_port()`.
        - A timeout of 100 seconds is set for the signal transmission.
    """
    signal_dic = dict()
    signal_dic['function'] = 'kill'
    signal_dic['work_env_id'] = work_env_id
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=100)


def kill_all():
    """
    Sends a signal to terminate all processes managed by the software server.

    This function constructs a signal dictionary with the function name 'kill_all'
    and sends it to the software server running on the localhost at the port
    specified by `environment.get_softwares_server_port()`. The signal is sent
    using the `socket_utils.send_signal` method with a timeout of 100 seconds.

    Returns:
        bool: True if the signal was successfully sent and acknowledged, False otherwise.
    """
    signal_dic = dict()
    signal_dic['function'] = 'kill_all'
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=100)


def died(work_env_id):
    """
    Sends a signal to notify that a specific work environment has terminated.

    Args:
        work_env_id (str): The identifier of the work environment that has died.

    Returns:
        bool: True if the signal was successfully sent, False otherwise.

    Raises:
        Exception: If there is an issue with sending the signal.

    Notes:
        This function uses `socket_utils.send_signal` to communicate with the
        software server, which is determined by `environment.get_softwares_server_port()`.
    """
    signal_dic = dict()
    signal_dic['function'] = 'died'
    signal_dic['work_env_id'] = work_env_id
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=0.5)


def get():
    """
    Sends a signal to the software server to perform a 'get' operation.

    This function constructs a signal dictionary with the function name 'get'
    and sends it to the software server using the `socket_utils.send_signal` method.
    The server address is determined by the localhost and the port retrieved
    from `environment.get_softwares_server_port()`. A timeout of 0.5 seconds
    is applied to the signal transmission.

    Returns:
        The response from the server after sending the signal.

    Raises:
        Any exceptions raised by `socket_utils.send_signal` if the operation fails.
    """
    signal_dic = dict()
    signal_dic['function'] = 'get'
    return socket_utils.send_signal(('localhost',
                                    environment.get_softwares_server_port()),
                                    signal_dic,
                                    timeout=0.5)


def core_kill_software_thread(software_thread):
    """
    Terminates the specified software thread.

    This function calls the `kill` method on the provided software thread
    object to terminate its execution.

    Args:
        software_thread: An object representing the software thread to be terminated.
                         It must have a `kill` method.

    Returns:
        The result of the `kill` method called on the software thread.

    Raises:
        AttributeError: If the provided software_thread does not have a `kill` method.
    """
    return software_thread.kill()


def core_launch_version(version_id):
    """
    Launches a specific version of a project in the appropriate software environment.

    Args:
        version_id (int): The ID of the version to be launched.

    Returns:
        tuple: A tuple containing:
            - thread (Thread or None): The thread running the software, or None if the launch failed.
            - work_env_id (int or None): The ID of the work environment, or None if the launch failed.

    Workflow:
        1. Retrieves version data for the given version ID.
        2. Validates the existence of the version and retrieves its file path and work environment ID.
        3. Adds the scene to the user's recent scenes list.
        4. Checks if the work environment is locked. If locked, the function exits.
        5. Locks the work environment to prevent concurrent access.
        6. Retrieves software information associated with the work environment.
        7. Builds the command and environment variables required to launch the software.
        8. Starts a new thread to launch the software with the constructed command and environment.
        9. Logs the launch event and returns the thread and work environment ID.

    Notes:
        - If any step in the process fails (e.g., missing data, invalid command), the function returns (None, None).
        - The function ensures that the work environment is locked during the launch process to avoid conflicts.
    """
    # Retrieve version data for the given version ID
    work_version_row = project.get_version_data(version_id)
    if not work_version_row:
        # If no version data is found, return None for both thread and work_env_id
        return None, None

    # Extract file path and work environment ID from the version data
    file_path = work_version_row['file_path']
    work_env_id = work_version_row['work_env_id']

    # Add the current work environment to the user's recent scenes list
    user.user().add_recent_scene((work_env_id, time.time()))

    # Check if the work environment is locked; if locked, return None
    if project.get_lock(work_env_id):
        return None, None

    # Lock the work environment to prevent concurrent access
    project.set_work_env_lock(work_env_id)

    # Retrieve software information associated with the work environment
    software_id = project.get_work_env_data(work_env_id, 'software_id')
    software_row = project.get_software_data(software_id)

    # Build the command to launch the software
    command = build_command(file_path, software_row, version_id)

    # Build the environment variables required for the software
    env = build_env(work_env_id, software_row, version_id)

    # If the command is invalid, return None
    if not command:
        return None, None

    # Create a new thread to launch the software with the constructed command and environment
    thread = software_thread(command,
                             env,
                             software_row['name'],
                             work_env_id)

    # Start the software thread
    thread.start()

    # Log the software launch event
    logger.info(f"{software_row['name']} launched")

    # Return the thread and work environment ID
    return thread, work_env_id


def build_command(file_path, software_row, version_id):
    """
    Constructs a command string to launch a software application with the specified file.
    Args:
        file_path (str): The path to the file to be opened by the software.
        software_row (dict): A dictionary containing software details, including:
            - 'path' (str): The path to the software executable.
            - 'name' (str): The name of the software.
            - 'file_command' (str): The command template for launching the software with a file.
            - 'no_file_command' (str): The command template for launching the software without a file.
        version_id (int): The version ID of the project, used to retrieve additional data.
    Returns:
        str: The constructed command string to launch the software, or None if the command cannot be built.
    Notes:
        - Logs warnings if the software path is invalid or not defined.
        - Handles specific launch requirements for Substance Painter, including resolving modeling references.
        - Replaces placeholders in the command template with actual values, such as the software path, file path, 
          and optional script paths.
    Raises:
        None: This function does not raise exceptions but logs warnings for invalid conditions.
    """
    # Retrieve the software executable path from the software_row dictionary
    software_path = software_row['path']

    # Check if the software executable exists at the specified path
    if not os.path.isfile(software_path):
        logger.warning(
            f"{software_row['name']} not found ( {software_path} does not exist )")
        return

    # Check if the software path is defined
    if software_path == '':
        logger.warning(f"{software_row['name']} path not defined")
        return

    # Determine the appropriate command template based on the file existence
    if path_utils.isfile(file_path):
        # Use the file command template
        raw_command = software_row['file_command']
    else:
        # Use the no-file command template
        raw_command = software_row['no_file_command']
        logger.info("File not existing, launching software with empty scene")

    # Replace placeholders in the command template with actual values
    raw_command = raw_command.replace(
        softwares_vars._executable_key_, software_path)
    raw_command = raw_command.replace(softwares_vars._file_key_, file_path)

    # Handle specific launch requirements for Substance Painter
    if software_row['name'] == softwares_vars._substance_painter_:
        work_env_id = project.get_version_data(version_id, 'work_env_id')
        references_dic = assets.get_references_files(work_env_id)

        # Check for modeling references and replace the reference key in the command
        if 'modeling' in references_dic.keys():
            reference_file = references_dic['modeling'][0]['files'][0]
            raw_command = raw_command.replace(softwares_vars._reference_key_,
                                              reference_file.replace('\\', '/'))
        else:
            logger.warning(
                'Please create ONE modeling reference to launch Substance Painter')

    # Handle script-specific requirements for certain software
    if software_row['name'] in softwares_vars._scripts_dic_.keys():
        raw_command = raw_command.replace(softwares_vars._script_key_,
                                          softwares_vars._scripts_dic_[software_row['name']])

    # Return the constructed command string
    return raw_command


def build_env(work_env_id, software_row, version_id, mode='gui'):
    """
    Builds and configures the environment variables for launching a specific software
    in a given work environment.
    Args:
        work_env_id (int): The ID of the work environment.
        software_row (dict): A dictionary containing information about the software,
            including its name and additional configuration.
        version_id (int): The version ID of the software to be launched.
        mode (str, optional): The launch mode for the software. Defaults to 'gui'.
    Returns:
        dict: A dictionary containing the configured environment variables.
    Environment Variables Set:
        - wizard_launch_mode: The launch mode (e.g., 'gui').
        - wizard_work_env_id: The ID of the work environment.
        - wizard_version_id: The version ID of the software.
        - wizard_variant_name: The name of the variant associated with the work environment.
        - wizard_stage_name: The name of the stage associated with the variant.
        - wizard_asset_name: The name of the asset associated with the stage.
        - wizard_category_name: The name of the category associated with the asset.
        - Software-specific environment variables for scripts and plugins.
    Notes:
        - Handles software-specific configurations for Substance Painter, Houdini, Nuke, and Maya.
        - Merges additional script paths and environment variables from the software configuration.
        - Cleans up specific environment variables related to QT and Python paths.
        - Removes any 'Wizard/_internal' paths from the PYTHONPATH variable.
    """
    # Copy the current environment variables
    env = os.environ.copy()

    # Set Wizard-specific environment variables
    env['wizard_launch_mode'] = mode
    env['wizard_work_env_id'] = str(work_env_id)
    env['wizard_version_id'] = str(version_id)

    # Retrieve and set variant, stage, asset, and category names
    variant_id = project.get_work_env_data(work_env_id, 'variant_id')
    variant_row = project.get_variant_data(variant_id)
    stage_id = project.get_variant_data(variant_id, 'stage_id')
    stage_row = project.get_stage_data(stage_id)
    asset_row = project.get_asset_data(stage_row['asset_id'])
    category_row = project.get_category_data(asset_row['category_id'])
    env['wizard_variant_name'] = str(variant_row['name'])
    env['wizard_stage_name'] = str(stage_row['name'])
    env['wizard_asset_name'] = str(asset_row['name'])
    env['wizard_category_name'] = str(category_row['name'])

    # Set script paths for the software
    env[softwares_vars._script_env_dic_[software_row['name']]
        ] = softwares_vars._main_script_path_
    env[softwares_vars._script_env_dic_[software_row['name']]
        ] += os.pathsep + project.get_hooks_folder()

    # Add Substance Painter-specific plugin paths
    if software_row['name'] == softwares_vars._substance_painter_:
        env[softwares_vars._script_env_dic_[software_row['name']]
            ] += os.pathsep + softwares_vars._plugins_path_[software_row['name']]

    # Add Houdini-specific menu path
    if software_row['name'] == softwares_vars._houdini_:
        env['HOUDINI_MENU_PATH'] = f"{softwares_vars._plugins_path_[software_row['name']]};&"

    # Add Nuke-specific plugin paths
    if software_row['name'] == softwares_vars._nuke_:
        if 'NUKE_PATH' in env.keys():
            env['NUKE_PATH'] += os.pathsep + \
                softwares_vars._plugins_path_[software_row['name']]

    # Remove OCIO environment variable for Maya
    if software_row['name'] == softwares_vars._maya_:
        if 'OCIO' in env.keys():
            del env['OCIO']

    # Add additional script paths and environment variables
    additionnal_script_paths = []
    if software_row['additionnal_scripts']:
        additionnal_script_paths = json.loads(
            software_row['additionnal_scripts'])
    additionnal_env = dict()
    if software_row['additionnal_env']:
        additionnal_env = json.loads(software_row['additionnal_env'])

    # Handle additional script paths
    if type(additionnal_script_paths) == str:
        additionnal_script_paths = additionnal_script_paths.split('\n')
    for script_path in additionnal_script_paths:
        env[softwares_vars._script_env_dic_[
            software_row['name']]] += os.pathsep+script_path

    # Merge additional environment variables
    for key in additionnal_env.keys():
        if key in env.keys():
            env[key] += os.pathsep+additionnal_env[key]
        else:
            env[key] = additionnal_env[key]

    # Clean up PYTHONPATH by removing any 'Wizard/_internal' paths
    if 'PYTHONPATH' in env.keys():
        python_path_list = env['PYTHONPATH'].split(';')
        for path in python_path_list:
            if 'Wizard/_internal' in path:
                python_path_list.remove(path)
        env['PYTHONPATH'] = (';').join(python_path_list)

    # Remove QT-related environment variables
    if 'QT_PLUGIN_PATH' in env.keys():
        del env['QT_PLUGIN_PATH']
    if 'QML2_IMPORT_PATH' in env.keys():
        del env['QML2_IMPORT_PATH']
    if 'QT_AUTO_SCREEN_SCALE_FACTOR' in env.keys():
        del env['QT_AUTO_SCREEN_SCALE_FACTOR']
    if 'QT_SCALE_FACTOR' in env.keys():
        del env['QT_SCALE_FACTOR']

    # Return the configured environment variables
    return env


class software_thread(Thread):
    """
    A thread class to manage the execution of a software process in a separate thread.
    Attributes:
        command (str): The command to execute the software.
        env (dict): The environment variables for the software process.
        software (str): The name of the software being executed.
        work_env_id (int): The ID of the working environment associated with the software.
        killed (bool): A flag indicating whether the process was killed.
        start_time (float): The time when the thread started execution.
    Methods:
        run():
            Executes the software process in a separate thread, waits for it to complete,
            and updates the UI and related information upon completion.
        set_infos():
            Updates the work environment lock, adds work time, and logs the closure of the software.
        kill():
            Terminates the software process, updates related information, and logs the termination.
    """

    def __init__(self, command, env, software, work_env_id):
        """
        Initializes a new instance of the software_thread class.

        Args:
            command (str): The command to be executed by the thread.
            env (dict): The environment variables to be used during execution.
            software (str): The name of the software associated with the thread.
            work_env_id (int): The identifier for the working environment.

        Attributes:
            command (str): Stores the command to be executed.
            env (dict): Stores the environment variables.
            software (str): Stores the name of the software.
            work_env_id (int): Stores the working environment identifier.
            killed (bool): Indicates whether the thread has been terminated.
            start_time (float): Records the start time of the thread execution.
        """
        super(software_thread, self).__init__()
        self.command = command
        self.env = env
        self.software = software
        self.work_env_id = work_env_id
        self.killed = False
        self.start_time = time.perf_counter()

        # Log the command and environment if the app is launched with the DEBUG argument
        logger.debug('_______________COMMAND_______________')
        logger.debug(self.command)
        logger.debug('_______________COMMAND_______________')
        logger.debug('_______________ENV_______________')
        for key in self.env.keys():
            logger.debug(f"{key} = {self.env[key]}")
        logger.debug('_______________ENV_______________')
        logger.debug('_______________PATH ENV_______________')
        for path in env['PATH'].split(';'):
            logger.debug(f"{path}")
        logger.debug('_______________PATH ENV_______________')

    def run(self):
        """
        Executes the specified command in a subprocess, waits for its completion, 
        and performs post-execution tasks such as updating the UI and setting 
        environment information.

        The function uses the `subprocess.Popen` method to run the command in a 
        specified environment and working directory. After the process completes, 
        it marks the environment as terminated and updates the UI if the process 
        was not manually killed.

        Attributes:
            self.command (str): The command to be executed.
            self.env (dict): The environment variables for the subprocess.
            self.work_env_id (int): The identifier for the working environment.
            self.killed (bool): A flag indicating whether the process was manually killed.

        Post-Execution:
            - Calls `died()` to mark the working environment as terminated.
            - If the process was not killed, updates environment information 
              and refreshes the GUI using `set_infos()` and `gui_server.refresh_ui()`.

        Raises:
            Any exceptions raised by `subprocess.Popen`, `shlex.split`, or 
            other invoked methods are not explicitly handled in this function.
        """
        self.process = subprocess.Popen(args=shlex.split(
            self.command), env=self.env, cwd=path_utils.abspath('softwares'))
        self.process.wait()
        died(self.work_env_id)
        if not self.killed:
            self.set_infos()
            gui_server.refresh_ui()

    def set_infos(self):
        """
        Updates and logs information related to the current work environment upon closure.

        This function performs the following actions:
        - Calculates the total work time by measuring the elapsed time since the start.
        - Unlocks the current work environment by setting its lock status to 0.
        - Records the work time for the current work environment.
        - Adds the current scene to the user's list of recently accessed scenes with a timestamp.
        - Logs a message indicating that the associated software has been closed.

        Attributes:
        - self.start_time (float): The start time of the work session.
        - self.work_env_id (int): The identifier for the current work environment.
        - self.software (str): The name of the software being used.

        Dependencies:
        - `time.perf_counter` for calculating elapsed time.
        - `project.set_work_env_lock` for unlocking the work environment.
        - `assets.add_work_time` for recording work time.
        - `user.user().add_recent_scene` for updating the user's recent scenes.
        - `logger.info` for logging the closure message.
        """
        work_time = time.perf_counter()-self.start_time
        project.set_work_env_lock(self.work_env_id, 0)
        assets.add_work_time(self.work_env_id, work_time)
        user.user().add_recent_scene((self.work_env_id, time.time()))
        logger.info(f"{self.software} closed")

    def kill(self):
        """
        Terminates the process associated with the software.

        This method forcefully kills the process, waits for it to terminate,
        updates the internal state to reflect that the process has been killed,
        and logs the action.

        Returns:
            int: Always returns 1 to indicate the process was killed.
        """
        self.process.kill()
        self.process.wait()
        self.killed = True
        self.set_infos()
        logger.info(f"{self.software} killed")
        return 1


class softwares_server(Thread):
    """
    A server class that manages software threads and handles communication
    through sockets. This class is responsible for launching, killing, and
    managing software instances in a multi-threaded environment.
    Attributes:
        port (int): The port number on which the server listens.
        server (socket.socket): The server socket instance.
        server_address (str): The address of the server.
        running (bool): A flag indicating whether the server is running.
        software_threads_dic (dict): A dictionary mapping work environment IDs
            to their corresponding software threads.
    Methods:
        run():
            Starts the server loop to accept and process incoming connections.
        stop():
            Stops the server and closes the socket.
        analyse_signal(signal_as_str, conn):
            Analyzes incoming signals and performs the corresponding actions.
        launch(version_id):
            Launches a new software thread for the given version ID.
        kill_all():
            Terminates all running software threads.
        kill(work_env_id):
            Terminates a specific software thread by its work environment ID.
        remove(work_env_id):
            Removes a software thread from the dictionary by its work environment ID.
    """

    def __init__(self):
        """
        Initializes the `softwares_server` class.

        This constructor sets up the server by obtaining an available port,
        configuring the environment with the server port, and initializing
        the server and its address. It also prepares the server to run and
        initializes a dictionary to manage software threads.

        Attributes:
            port (int): The port number assigned to the server.
            server (socket.socket): The server socket instance.
            server_address (tuple): The address of the server as a tuple (host, port).
            running (bool): A flag indicating whether the server is running.
            software_threads_dic (dict): A dictionary to store software threads.
        """
        super(softwares_server, self).__init__()
        self.port = socket_utils.get_port('localhost')
        environment.set_softwares_server_port(self.port)
        self.server, self.server_address = socket_utils.get_server(('localhost',
                                                                    self.port))
        self.running = True
        self.software_threads_dic = dict()

    def run(self):
        """
        Continuously listens for incoming connections and processes signals.

        This method runs in a loop while the `self.running` flag is set to True.
        It accepts incoming connections from the server socket, verifies the
        address of the connection, and processes the received signal if valid.

        Exceptions:
            - OSError: Silently ignored, typically occurs during socket operations.
            - Any other exception: Logged with a traceback for debugging purposes.

        Workflow:
            1. Accepts a connection from the server socket.
            2. Verifies if the connection's address matches the expected server address.
            3. Receives the signal as a string from the connection.
            4. If a valid signal is received, it is analyzed using `self.analyse_signal`.

        Note:
            - The method relies on `socket_utils.recvall` to receive the complete signal.
            - The signal is expected to be UTF-8 encoded.
            - Logging is used to capture unexpected errors for debugging.
        """
        while self.running:
            try:
                conn, addr = self.server.accept()
                if addr[0] != self.server_address:
                    continue
                signal_as_str = socket_utils.recvall(conn)
                if not signal_as_str:
                    continue
                self.analyse_signal(signal_as_str.decode('utf8'), conn)
            except OSError:
                pass
            except:
                logger.error(str(traceback.format_exc()))

    def stop(self):
        """
        Stops the server and updates the running status.

        This method closes the server connection and sets the `running` attribute
        to `False`, effectively stopping the server's operation.
        """
        self.server.close()
        self.running = False

    def analyse_signal(self, signal_as_str, conn):
        """
        Analyzes the incoming signal and performs the corresponding action based on the signal's function.
        Args:
            signal_as_str (str): The signal data in JSON string format, containing the function to execute and its parameters.
            conn: The connection object used to send the response back.
        Returns:
            None: The result of the executed function is sent back through the provided connection.
        Signal Functions:
            - 'launch': Launches a process with the specified version ID.
            - 'kill': Terminates a process with the specified work environment ID.
            - 'kill_all': Terminates all running processes.
            - 'get': Retrieves a list of all active software thread keys.
            - 'died': Removes a process with the specified work environment ID.
        Note:
            The result of the executed function is sent back using `socket_utils.send_signal_with_conn`.
        """
        returned = 0
        signal_dic = json.loads(signal_as_str)

        if signal_dic['function'] == 'launch':
            returned = self.launch(signal_dic['version_id'])
        if signal_dic['function'] == 'kill':
            returned = self.kill(signal_dic['work_env_id'])
        if signal_dic['function'] == 'kill_all':
            returned = self.kill_all()
        if signal_dic['function'] == 'get':
            returned = list(self.software_threads_dic.keys())
        if signal_dic['function'] == 'died':
            returned = self.remove(signal_dic['work_env_id'])

        socket_utils.send_signal_with_conn(conn, returned)

    def launch(self, version_id):
        """
        Launches a work environment for the specified version ID.

        Args:
            version_id (str): The ID of the version to launch.

        Returns:
            str or None: The work environment ID if successfully launched, 
                         otherwise None.

        Behavior:
            - Retrieves the work environment ID associated with the given version ID.
            - If no work environment ID is found, the function exits early.
            - Checks if the work environment is already running. If so, logs a warning
              and exits without launching a new instance.
            - Launches the version using `core_launch_version` and stores the resulting
              software thread in `self.software_threads_dic` if successful.
        """
        work_env_id = project.get_version_data(version_id, 'work_env_id')
        if not work_env_id:
            return
        if work_env_id in self.software_threads_dic.keys():
            logger.warning(
                f"You are already running a work instance of this asset")
            return
        software_thread, work_env_id = core_launch_version(version_id)
        if software_thread is not None:
            self.software_threads_dic[work_env_id] = software_thread
        return work_env_id

    def kill_all(self):
        """
        Terminates all software threads managed by the instance.

        This method retrieves all thread IDs from the `software_threads_dic` dictionary
        and iteratively calls the `kill` method for each thread ID to terminate them.

        Returns:
            int: Returns 1 after all threads have been terminated.

        Notes:
            - If `software_threads_dic` is empty or None, the method exits early without performing any action.
        """
        software_threads_ids = list(self.software_threads_dic.keys())
        if software_threads_ids is None:
            return
        for work_env_id in software_threads_ids:
            self.kill(work_env_id)
        return 1

    def kill(self, work_env_id):
        """
        Terminates a running software thread associated with the given work environment ID.

        Args:
            work_env_id (str): The identifier of the work environment whose software thread 
                               needs to be terminated.

        Returns:
            bool: True if the software thread was successfully terminated, False otherwise.

        Logs:
            - Logs a warning if the specified work environment ID is not found or not running.
        """
        if work_env_id not in self.software_threads_dic.keys():
            logger.warning("Work environment not running or not found")
            return
        software_thread = self.software_threads_dic[work_env_id]
        self.remove(work_env_id)
        return core_kill_software_thread(software_thread)

    def remove(self, work_env_id):
        """
        Removes a software thread entry from the dictionary based on the given work environment ID.

        Args:
            work_env_id (str): The identifier of the work environment to be removed.

        Returns:
            int: Always returns 1 after attempting to remove the entry.
        """
        if work_env_id in self.software_threads_dic.keys():
            del self.software_threads_dic[work_env_id]
        return 1
