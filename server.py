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
This module implements a multi-threaded server for managing client connections,
broadcasting messages, and handling various client-server interactions.

The server is designed to:
- Accept and manage multiple client connections.
- Broadcast messages between clients.
- Handle specific client requests such as adding new clients, removing clients,
    and sending targeted messages.

Key Features:
- Threaded server implementation for handling multiple clients simultaneously.
- Logging support for debugging and monitoring server activity.
- JSON-based message serialization and deserialization.
- Robust error handling for socket operations.

Classes:
- server: A threaded server class for managing client connections and interactions.

Functions:
- get_server(DNS): Creates and returns a server socket bound to the specified DNS address.
- send_signal_with_conn(conn, msg_raw, only_debug): Sends a serialized message through a socket connection.
- recvall(sock): Receives a complete message from a socket.
- recvall_with_given_len(sock, n): Receives a specified number of bytes from a socket.

Usage:
Run this script directly to start the server. The server listens for incoming
connections on the specified IP address and port, and handles client interactions
in separate threads.
"""

# Python modules
import socket
import sys
import threading
import time
import traceback
import json
import logging
from logging.handlers import RotatingFileHandler
import os
import struct

host_name = socket.gethostname()
local_ip = socket.gethostbyname(host_name)

ip_address = local_ip
port = 50333

# create logger
logger = logging.getLogger('WIZARD-SERVER')
logger.setLevel(logging.DEBUG)

user_path = os.path.expanduser('~/Documents/wizard/')
if not os.path.isdir(user_path):
    os.mkdir(user_path)
log_file = os.path.join(user_path, "wizard_server.log")
# create file handler and set level to debug
file_handler = RotatingFileHandler(
    log_file, mode='a', maxBytes=1000000, backupCount=1000, encoding=None, delay=False)
# create console handler and set level to debug
stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
# create formatter
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# add formatter to handlers
stream_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)
# add handlers to logger
logger.addHandler(stream_handler)
logger.addHandler(file_handler)
logger.info("Python : " + str(sys.version))


def get_server(DNS):
    """
    Creates and returns a server socket bound to the specified DNS address.

    Args:
        DNS (tuple): A tuple containing the host (str) and port (int) to bind the server socket to.

    Returns:
        tuple or None: A tuple containing the server socket object and the resolved server address (str),
                       or None if an error occurs during socket creation or binding.

    Exceptions Handled:
        - ConnectionRefusedError: Logs a debug message if the connection is refused.
        - socket.timeout: Logs a debug message if the socket operation times out.
        - Other exceptions: Logs the traceback of any other exceptions that occur.

    Notes:
        - The server socket is configured to reuse the address (SO_REUSEADDR).
        - The server listens for up to 100 incoming connections.
    """
    server = None
    server_address = None
    try:
        server_address = socket.gethostbyname(DNS[0])
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(DNS)
        server.listen(100)
    except ConnectionRefusedError:
        logger.debug(
            f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None
    except socket.timeout:
        logger.debug(
            f"Socket timeout")
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return server, server_address


def send_signal_with_conn(conn, msg_raw, only_debug=False):
    """
    Sends a serialized message through a socket connection.

    This function serializes the given message, prefixes it with its length,
    and sends it through the provided socket connection. It handles various
    exceptions that may occur during the process and logs them accordingly.

    Args:
        conn (socket.socket): The socket connection through which the message
            will be sent.
        msg_raw (dict): The raw message to be serialized and sent.
        only_debug (bool, optional): If True, logs errors as debug messages
            instead of error messages. Defaults to False.

    Returns:
        int: Returns 1 if the message is successfully sent.
        None: Returns None if an exception occurs during the process.

    Exceptions Handled:
        - ConnectionRefusedError: Raised when the connection is refused.
        - socket.timeout: Raised when the socket operation times out.
        - Other exceptions: Any other exceptions are caught and logged.
    """
    try:
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        conn.sendall(msg)
        return 1
    except ConnectionRefusedError:
        if only_debug:
            logger.debug(
                f"Socket connection refused")
        else:
            logger.error(
                f"Socket connection refused")
        return None
    except socket.timeout:
        if only_debug:
            logger.debug(
                f"Socket timeout")
        else:
            logger.error(
                f"Socket timeout")
        return None
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return None


def recvall(sock):
    """
    Receives a complete message from a socket.

    This function reads a message from the given socket by first reading the 
    length of the message (4 bytes, big-endian format) and then reading the 
    actual message content based on the length. It handles various exceptions 
    such as connection refusal, socket timeout, and other unexpected errors.

    Args:
        sock (socket.socket): The socket object from which to receive the message.

    Returns:
        bytes: The complete message received from the socket, or None if an 
        error occurs or the connection is refused.

    Exceptions Handled:
        - ConnectionRefusedError: Logs a debug message if the connection is refused.
        - socket.timeout: Logs a debug message if the socket operation times out.
        - Other exceptions: Logs the traceback of the exception for debugging purposes.
    """
    try:
        raw_msglen = recvall_with_given_len(sock, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall_with_given_len(sock, msglen)
    except ConnectionRefusedError:
        logger.debug(
            f"Socket connection refused")
        return None
    except socket.timeout:
        logger.debug(
            f"Socket timeout")
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None


def recvall_with_given_len(sock, n):
    """
    Receives a specified number of bytes from a socket.

    This function attempts to read exactly `n` bytes of data from the given socket.
    It handles partial reads by repeatedly calling `recv` until the desired amount
    of data is received or an error occurs.

    Args:
        sock (socket.socket): The socket object to read data from.
        n (int): The number of bytes to receive.

    Returns:
        bytearray: The received data as a bytearray if successful.
        None: If the connection is refused, times out, or any other error occurs.

    Exceptions Handled:
        - ConnectionRefusedError: Logs a debug message if the connection is refused.
        - socket.timeout: Logs a debug message if the socket operation times out.
        - Any other exception: Logs the traceback of the exception.

    Note:
        If the connection is closed by the peer before `n` bytes are received,
        the function will return `None`.
    """
    try:
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data.extend(packet)
        return data
    except ConnectionRefusedError:
        logger.debug(
            f"Socket connection refused")
        return None
    except socket.timeout:
        logger.debug(
            f"Socket timeout")
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return data


class server(threading.Thread):
    """
    A server class that extends threading.Thread to handle client connections, 
    manage client data, and broadcast messages between clients.
    Attributes:
        server (socket): The server socket object.
        server_adress (tuple): The address of the server (IP and port).
        client_ids (dict): A dictionary to store client information, 
            where keys are client IDs and values are dictionaries containing 
            client details (e.g., username, connection, address, project).
    Methods:
        __init__():
            Initializes the server, sets up the server socket, and logs server details.
        run():
            Continuously listens for incoming client connections and processes their messages.
        analyse_signal(msg_raw, conn, addr):
            Analyzes incoming messages from clients and performs actions based on the message type.
        add_client(user_name, conn, addr, project):
            Adds a new client to the server, starts a thread for the client, 
            and broadcasts the new user's information to other clients.
        send_users_to_new_client(client_dic):
            Sends the list of existing users to a newly connected client.
        clientThread(client_id, user_name, conn, addr, project):
            Handles communication with a specific client in a separate thread.
        broadcast(data, client_dic):
            Broadcasts a message to all connected clients except the sender.
        remove_client(client_dic):
            Removes a client from the server, closes their connection, 
            and notifies other clients about the removal.
    """

    def __init__(self):
        """
        Initializes the server instance.

        This constructor sets up the server by:
        - Logging the server's IP address and default port.
        - Creating a server socket using the `get_server` function.
        - Initializing a dictionary to store client information.

        Behavior:
            - Calls the parent class's `__init__` method to initialize the thread.
            - Logs the server's startup details.
            - Binds the server to the specified IP address and port.
            - Prepares the server to accept client connections.

        Attributes:
            self.server (socket): The server socket object.
            self.server_adress (tuple): The address of the server (IP and port).
            self.client_ids (dict): A dictionary to store connected client information.

        Note:
            If the server fails to start, the `get_server` function will return `None`.
        """
        super(server, self).__init__()
        logger.info("Starting server on : '" + str(ip_address) + "'")
        logger.info("Default port : '" + str(port) + "'")
        self.server, self.server_adress = get_server((ip_address, port))
        logger.info("Server started")
        self.client_ids = dict()

    def run(self):
        """
        Main loop for the server thread.

        This method continuously listens for incoming client connections,
        receives their initial message, and processes it using the `analyse_signal` method.

        Behavior:
            - Accepts incoming client connections using the server socket.
            - Receives the initial message from the client using the `recvall` function.
            - Analyzes the received message and performs actions based on its content.
            - Logs any exceptions that occur during the process.

        Note:
            This method runs indefinitely until the server is stopped.
        """
        while True:
            try:
                # Accept a new client connection
                conn, addr = self.server.accept()
                # Receive the initial message from the client
                entry_message = recvall(conn)
                # Analyze the received message and take appropriate action
                self.analyse_signal(entry_message, conn, addr)
            except:
                # Log any exceptions that occur during the process
                logger.error(str(traceback.format_exc()))
                continue

    def analyse_signal(self, msg_raw, conn, addr):
        """
        Analyzes the incoming signal message and performs actions based on its type.

        Args:
            msg_raw (str): The raw JSON string containing the signal message.
            conn (socket.socket): The connection object associated with the client.
            addr (tuple): The address of the client.

        Behavior:
            - If the message type is 'test_conn', logs a connection test message.
            - If the message type is 'new_client', adds a new client to the server with the provided details.
            - If the message type is 'prank', attempts to find the destination user and broadcasts the prank data
              if the user exists. Sends a success or failure signal back to the sender.
            - For other message types, broadcasts the data to all clients.

        Note:
            - The `self.add_client` method is used to register new clients.
            - The `self.broadcast` method is used to send messages to all clients.
            - The `send_signal_with_conn` function is used to send a response back to the sender.
        """
        data = json.loads(msg_raw)
        if data['type'] == 'test_conn':
            logger.info('test_conn')
        elif data['type'] == 'new_client':
            self.add_client(data['user_name'], conn, addr, data['project'])
        elif data['type'] == 'prank':
            client_id = next((client_id for client_id, client_dic in self.client_ids.items(
            ) if client_dic['user_name'] == data['prank_data']['destination_user']), None)
            if client_id:
                client_dic = dict()
                client_dic['id'] = None
                send_signal_with_conn(conn, True)
                self.broadcast(data, client_dic)
            else:
                send_signal_with_conn(conn, False)
        else:
            client_dic = dict()
            client_dic['id'] = None
            self.broadcast(data, client_dic)

    def add_client(self, user_name, conn, addr, project):
        """
        Adds a new client to the server, initializes their information, and starts a thread to handle client communication.
        Args:
            user_name (str): The username of the client.
            conn (socket.socket): The socket connection object for the client.
            addr (tuple): The address of the client (IP, port).
            project (str): The project associated with the client.
        Functionality:
            - Creates a dictionary to store client details, including a unique client ID.
            - Adds the client to the server's client list.
            - Starts a new thread to handle communication with the client.
            - Logs the addition of the new client.
            - Broadcasts a signal to notify other clients of the new user.
            - Sends the list of existing users to the newly added client.
        """
        client_dic = dict()
        client_dic['user_name'] = user_name
        client_dic['conn'] = conn
        client_dic['addr'] = addr
        client_dic['project'] = project
        client_id = str(time.time())
        client_dic['id'] = client_id
        self.client_ids[client_id] = client_dic

        threading.Thread(target=self.clientThread, args=(
            client_id, user_name, conn, addr, project)).start()
        logger.info("New client : {}, {}, {}, {}".format(
            client_id, user_name, addr, project))
        signal_dic = dict()
        signal_dic['type'] = 'new_user'
        signal_dic['user_name'] = user_name
        signal_dic['project'] = project
        self.broadcast(signal_dic, self.client_ids[client_id])
        self.send_users_to_new_client(client_dic)

    def send_users_to_new_client(self, client_dic):
        """
        Sends information about existing users to a newly connected client.

        This method iterates through the list of connected clients and sends
        a signal to the new client containing details about each existing user,
        except the new client itself.

        Args:
            client_dic (dict): A dictionary containing information about the new client.
                Expected keys:
                    - 'id': The unique identifier of the new client.
                    - 'conn': The connection object for the new client.

        Behavior:
            - For each existing client in `self.client_ids`, if the client is not the
              new client (based on the 'id'), a signal dictionary is created with the
              following keys:
                - 'type': Set to 'new_user'.
                - 'user_name': The username of the existing client.
                - 'project': The project associated with the existing client.
            - The signal dictionary is sent to the new client using the provided
              connection object (`client_dic['conn']`).

        Note:
            This function assumes the existence of a `send_signal_with_conn` function
            that handles sending signals over a connection.
        """
        for client in self.client_ids.keys():
            if client != client_dic['id']:
                signal_dic = dict()
                signal_dic['type'] = 'new_user'
                signal_dic['user_name'] = self.client_ids[client]['user_name']
                signal_dic['project'] = self.client_ids[client]['project']
                send_signal_with_conn(client_dic['conn'], signal_dic)

    def clientThread(self, client_id, user_name, conn, addr, project):
        """
        Handles communication with a connected client in a separate thread.

        Args:
            client_id (int): The unique identifier for the client.
            user_name (str): The username of the connected client.
            conn (socket.socket): The socket connection object for the client.
            addr (tuple): The address of the connected client (IP, port).
            project (str): The project associated with the client.

        Functionality:
            - Initializes a dictionary to store client details.
            - Continuously listens for incoming data from the client.
            - Parses received data as JSON and broadcasts it to other clients.
            - Removes the client from the active client list if the connection is lost.
            - Logs any exceptions that occur during communication.

        Note:
            This function runs in a loop until the client disconnects or an error occurs.
        """
        client_dic = dict()
        client_dic['id'] = client_id
        client_dic['user_name'] = user_name
        client_dic['conn'] = conn
        client_dic['addr'] = addr
        client_dic['project'] = project
        running = True
        while running:
            try:
                raw_data = recvall(client_dic['conn'])
                if raw_data is not None:
                    data = json.loads(raw_data)
                    self.broadcast(data, client_dic)
                else:
                    if conn is not None:
                        self.remove_client(client_dic)
                        running = False
            except:
                logger.error(str(traceback.format_exc()))
                continue

    def broadcast(self, data, client_dic):
        """
        Broadcasts a message to all connected clients except the sender.

        Args:
            data (any): The data to be broadcasted to the clients.
            client_dic (dict): A dictionary containing information about the sender client, 
                               including its unique 'id'.

        Behavior:
            - Logs the broadcasted data for debugging purposes.
            - Iterates through all connected clients and sends the data to each client 
              except the sender.
            - If sending the data to a client fails, removes the client from the list 
              of connected clients.

        Note:
            The `send_signal_with_conn` function is used to send the data to a client, 
            and the `remove_client` method is called to handle disconnections.
        """
        logger.debug("Broadcasting : " + str(data))
        for client in self.client_ids.keys():
            if client != client_dic['id']:
                if not send_signal_with_conn(self.client_ids[client]['conn'], data):
                    self.remove_client(self.client_ids[client])

    def remove_client(self, client_dic):
        """
        Removes a client from the server's client list and notifies other clients.

        Args:
            client_dic (dict): A dictionary containing client information with the following keys:
                - 'id' (str): The unique identifier of the client.
                - 'user_name' (str): The username of the client.
                - 'addr' (tuple): The address of the client (IP, port).
                - 'project' (str): The project associated with the client.
                - 'conn' (socket): The connection object for the client.

        Behavior:
            - Logs the removal of the client.
            - Deletes the client from the server's client list (`self.client_ids`).
            - Closes the client's connection.
            - Broadcasts a signal to notify other clients about the removal, including the username and project.

        Raises:
            KeyError: If the client's ID is not found in the server's client list.
        """
        if client_dic['id'] in self.client_ids.keys():
            logger.info("Removing client : {}, {}, {}, {}".format(
                client_dic['id'], client_dic['user_name'], client_dic['addr'], client_dic['project']))
            del self.client_ids[client_dic['id']]
            client_dic['conn'].close()
            signal_dic = dict()
            signal_dic['type'] = 'remove_user'
            signal_dic['user_name'] = client_dic['user_name']
            signal_dic['project'] = client_dic['project']
            self.broadcast(signal_dic, client_dic)


if __name__ == "__main__":
    try:
        server = server()
        server.daemon = True
        server.start()
        print('Press Ctrl+C to quit...')
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        print('Stopping server...')
        raise SystemExit
        sys.exit()
