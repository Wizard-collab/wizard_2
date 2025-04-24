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
This module provides the implementation of the `team_client` class and related functions 
to manage communication with a team server. It uses PyQt6 for signal handling and threading 
and includes methods for establishing connections, sending signals, and processing incoming data.

Classes:
    - team_client: A subclass of QThread that manages the connection and communication 
      with a team server. It includes methods for initializing connections, sending signals, 
      and analyzing incoming data.

Functions:
    - try_connection(DNS): Attempts to establish a connection to the specified DNS using a test signal.
    - refresh_team(DNS): Sends a signal to refresh the team information for the specified DNS.
    - send_prank(DNS, prank_data): Sends a prank signal to the specified DNS with the provided prank data.

Dependencies:
    - PyQt6.QtCore: For signal handling and threading.
    - json: For parsing and handling JSON data.
    - logging: For logging messages.
    - wizard.core.socket_utils: For socket communication utilities.
    - wizard.core.environment: For retrieving environment-specific information like DNS, user, and project name.

Usage:
    This module is designed to be used as part of the Wizard application for managing 
    team communication and collaboration. The `team_client` class can be instantiated 
    and run in a separate thread to handle server communication in the background.
"""

# Python modules
from PyQt6.QtCore import pyqtSignal, QThread
import json
import logging

# Wizard modules
from wizard.core import socket_utils
from wizard.core import environment

logger = logging.getLogger(__name__)


class team_client(QThread):
    """
    team_client is a subclass of QThread that manages the connection and communication 
    with a team server. It handles sending and receiving signals, maintaining the 
    connection, and processing incoming data.
    Attributes:
        team_connection_status_signal (pyqtSignal): Signal emitted to indicate the 
            connection status (True for connected, False for disconnected).
        refresh_signal (pyqtSignal): Signal emitted to trigger a refresh operation, 
            passing an integer as a parameter.
        prank_signal (pyqtSignal): Signal emitted when prank data is received, passing 
            the prank data as an object.
        new_user_signal (pyqtSignal): Signal emitted when a new user joins, passing 
            the username as a string.
        remove_user_signal (pyqtSignal): Signal emitted when a user is removed, passing 
            the username as a string.
    Methods:
        __init__():
            Initializes the team_client instance and sets up the connection attribute.
        create_conn():
            Establishes a connection to the team server using the DNS provided by the 
            environment. Initializes the connection if successful.
        init_conn():
            Sends an initial signal to the server to register the client with its 
            username and project information.
        stop():
            Stops the thread, closes the connection, and cleans up resources.
        refresh_team():
            Sends a signal to the server to request a team refresh for the current project.
        send_signal(signal_dic):
            Sends a signal dictionary to the server. Stops the connection if sending fails.
        run():
            Main thread execution method. Continuously listens for incoming data from 
            the server, processes it, and emits appropriate signals.
        analyse_signal(data):
            Analyzes incoming data from the server and emits corresponding signals 
            based on the type of data received.
    """

    team_connection_status_signal = pyqtSignal(bool)
    refresh_signal = pyqtSignal(int)
    prank_signal = pyqtSignal(object)
    new_user_signal = pyqtSignal(str)
    remove_user_signal = pyqtSignal(str)

    def __init__(self):
        """
        Initializes an instance of the `team_client` class.

        This constructor sets up the initial state of the object by initializing
        the `conn` attribute to `None` and calling the constructor of the parent class.
        """
        self.conn = None
        super(team_client, self).__init__()

    def create_conn(self):
        """
        Establishes a connection to the team server.

        This method initializes a connection to the team server using the DNS
        retrieved from the environment. If the DNS is available, it attempts to
        create a connection using the `socket_utils.get_connection` method. If
        the connection is successfully established, it initializes the connection
        by calling `init_conn`. If the DNS is not available or the connection
        cannot be established, the connection attribute (`self.conn`) is set to None.

        Attributes:
            self.running (bool): Indicates whether the connection process is active.
            self.conn (object or None): The connection object if successfully established,
                                        otherwise None.
        """
        self.running = True
        team_dns = environment.get_team_dns()
        if team_dns is not None:
            self.conn = socket_utils.get_connection(team_dns)
        else:
            self.conn = None
        if self.conn is not None:
            self.init_conn()

    def init_conn(self):
        """
        Initializes a connection to the team server.

        This method creates a signal dictionary containing information about the 
        client, such as the user name and project name, and sends it to the server 
        using the provided connection. Logs a message indicating that the wizard 
        is connected to the team server.

        Returns:
            None
        """
        signal_dic = dict()
        signal_dic['type'] = 'new_client'
        signal_dic['user_name'] = environment.get_user()
        signal_dic['project'] = environment.get_project_name()
        socket_utils.send_signal_with_conn(self.conn, signal_dic)
        logger.info("Wizard is connected to the team server")

    def stop(self):
        """
        Stops the current operation by setting the running flag to False and closing the connection if it exists.

        This method ensures that the connection is properly closed and cleaned up by setting it to None after closing.

        Attributes:
            self.running (bool): A flag indicating whether the operation is running.
            self.conn (object): The connection object to be closed, if it exists.
        """
        self.running = False
        if self.conn is not None:
            self.conn.close()
            self.conn = None

    def refresh_team(self):
        """
        Refreshes the team information by sending a signal with the relevant details.

        This method constructs a signal dictionary containing the type of signal 
        ('refresh_team') and the current project name. It then sends this signal 
        using the `send_signal` method.

        Returns:
            None
        """
        signal_dic = dict()
        signal_dic['type'] = 'refresh_team'
        signal_dic['project'] = environment.get_project_name()
        self.send_signal(signal_dic)

    def send_signal(self, signal_dic):
        """
        Sends a signal to the connected client using the established connection.

        Args:
            signal_dic (dict): A dictionary containing the signal data to be sent.

        Behavior:
            - If a connection (`self.conn`) exists, it attempts to send the signal
              using `socket_utils.send_signal_with_conn`.
            - If the signal fails to send (returns False), the connection is stopped
              by calling `self.stop()`.

        Note:
            The `only_debug` parameter in `send_signal_with_conn` is set to True,
            which may affect how the signal is processed or logged.
        """
        if self.conn is not None:
            if not socket_utils.send_signal_with_conn(self.conn, signal_dic, only_debug=True):
                self.stop()

    def run(self):
        """
        Executes the main loop for managing the team client connection.

        This method establishes a connection, emits a signal indicating the connection
        status, and continuously listens for incoming data while the connection is active
        and the client is running. Incoming data is processed and analyzed if valid JSON
        is received. If the connection is closed or invalid data is encountered, appropriate
        actions are taken.

        Emits:
            team_connection_status_signal (bool): Emits `True` when the connection is established
            and `False` when the connection is closed.

        Raises:
            json.decoder.JSONDecodeError: Logs a debug message if the received data cannot
            be parsed as JSON.

        Notes:
            - The method stops execution if `self.running` is set to `False` or the connection
              (`self.conn`) is closed.
            - The `analyse_signal` method is called with the parsed JSON data for further processing.
        """
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
            else:
                if self.running != True:
                    logger.info('Team connection closed')
                    self.stop()
        self.team_connection_status_signal.emit(False)

    def analyse_signal(self, data):
        """
        Analyzes the incoming signal data and emits the appropriate signal based on its type.

        Args:
            data (dict): A dictionary containing signal data. Expected keys include:
                - 'project' (str): The project name associated with the signal.
                - 'type' (str): The type of signal. Possible values are:
                    - 'refresh_team': Emits a signal to refresh the team.
                    - 'new_user': Emits a signal for adding a new user, with 'user_name' key in data.
                    - 'remove_user': Emits a signal for removing a user, with 'user_name' key in data.
                    - 'prank': Emits a prank signal if the 'destination_user' matches the current user.
                - 'prank_data' (dict, optional): Contains prank-specific data, including:
                    - 'destination_user' (str): The user targeted by the prank.

        Returns:
            None
        """
        if 'project' in data.keys():
            if data['project'] != environment.get_project_name():
                return
            if data['type'] == 'refresh_team':
                self.refresh_signal.emit(1)
            elif data['type'] == 'new_user':
                self.new_user_signal.emit(data['user_name'])
            elif data['type'] == 'remove_user':
                self.remove_user_signal.emit(data['user_name'])
        if data['type'] == 'prank' and (data['prank_data']['destination_user'] == environment.get_user()):
            self.prank_signal.emit(data['prank_data'])


def try_connection(DNS):
    """
    Attempts to establish a connection to the specified DNS using a test signal.

    This function sends a test signal dictionary with a type of 'test_conn' 
    to the given DNS using the `socket_utils.send_bottle` method. The function 
    includes a timeout of 1 second for the connection attempt.

    Args:
        DNS (str): The domain name or IP address to which the connection is attempted.

    Returns:
        bool: True if the connection is successful, False otherwise.
    """
    signal_dic = dict()
    signal_dic['type'] = 'test_conn'
    return socket_utils.send_bottle(DNS, signal_dic, timeout=1)


def refresh_team(DNS):
    """
    Sends a signal to refresh the team information for the specified DNS.

    Args:
        DNS (str): The domain name or address of the target server.

    Returns:
        Any: The response from the `socket_utils.send_bottle` function.

    Notes:
        - The signal dictionary includes the type of operation ('refresh_team') 
          and the current project name retrieved from the environment.
        - This function relies on `environment.get_project_name()` and 
          `socket_utils.send_bottle()` for its operation.
    """
    signal_dic = dict()
    signal_dic['type'] = 'refresh_team'
    signal_dic['project'] = environment.get_project_name()
    return socket_utils.send_bottle(DNS, signal_dic)


def send_prank(DNS, prank_data):
    """
    Sends a prank signal to the specified DNS with the provided prank data.

    Args:
        DNS (str): The destination DNS address to which the prank signal will be sent.
        prank_data (dict): A dictionary containing the data related to the prank.

    Returns:
        Any: The response from the `socket_utils.send_signal` function, which handles the signal transmission.
    """
    signal_dic = dict()
    signal_dic['type'] = 'prank'
    signal_dic['prank_data'] = prank_data
    return socket_utils.send_signal(DNS, signal_dic)
