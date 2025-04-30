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
This module provides utility functions for working with sockets, including
establishing connections, creating servers, sending and receiving messages,
and handling various socket-related exceptions.

Functions:
- get_connection: Establishes a socket connection to a specified DNS address and port.
- get_server: Creates and returns a server socket bound to a specified DNS address.
- send_bottle: Sends a serialized message to a server using a TCP socket.
- send_signal: Sends a signal to a server and waits for a JSON-encoded response.
- send_signal_with_conn: Sends a signal/message through an existing socket connection.
- recvall: Receives a complete message from a socket by reading its length and content.
- recvall_with_given_len: Receives a specified number of bytes from a socket.

Logging:
- Uses the `logging` module to log debug, info, and error messages based on the context.
- Handles exceptions gracefully and logs appropriate messages for debugging.

Notes:
- The module is compatible with both Python 2 and Python 3.
- Includes exception handling for `ConnectionRefusedError`, `socket.timeout`, and other generic exceptions.
"""

# Python modules
import socket
import json
import traceback
import struct
import sys
import logging

logger = logging.getLogger(__name__)

# Handle ConnectionRefusedError in python 2
if sys.version_info[0] == 2:
    from socket import error as ConnectionRefusedError


def get_connection(DNS, timeout=5.0, only_debug=False):
    """
    Establishes a socket connection to the specified DNS address and port.

    Args:
        DNS (tuple): A tuple containing the host (str) and port (int) to connect to.
        timeout (float, optional): The timeout duration for the connection in seconds. Defaults to 5.0.
        only_debug (bool, optional): If True, logs messages at the debug level. Otherwise, logs at the error level. Defaults to False.

    Returns:
        socket.socket or None: Returns the socket connection object if successful, or None if the connection fails.

    Exceptions Handled:
        - ConnectionRefusedError: Logs a message if the connection is refused.
        - socket.timeout: Logs a message if the connection times out.
        - Other exceptions: Logs the traceback of any other exceptions encountered.

    Note:
        Logging behavior is determined by the `only_debug` parameter. If `only_debug` is True, debug-level logs are used; otherwise, error-level logs are used.
    """
    connection = None
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect((DNS[0], DNS[1]))
        return connection
    except ConnectionRefusedError:
        if only_debug:
            logger.debug(
                "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        else:
            logger.error(
                "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        if only_debug:
            logger.debug(
                "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        else:
            logger.error(
                "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return None


def get_server(DNS):
    """
    Creates and returns a server socket bound to the specified DNS address.

    Args:
        DNS (tuple): A tuple containing the host (str) and port (int) to bind the server socket to.

    Returns:
        tuple or None: A tuple containing the server socket object and the server address (str) if successful,
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
            "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug(
            "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return server, server_address


def send_bottle(DNS, msg_raw, timeout=0.01):
    """
    Sends a serialized message to a specified server using a TCP socket.

    Args:
        DNS (tuple): A tuple containing the host (str) and port (int) of the server.
        msg_raw (dict): The raw message to be sent, which will be serialized to JSON.
        timeout (float, optional): The timeout duration for the socket connection in seconds. Defaults to 0.01.

    Returns:
        int: Returns 1 if the message is successfully sent.
        None: Returns None if there is a connection error, timeout, or any other exception.

    Exceptions Handled:
        - ConnectionRefusedError: Logs a debug message if the connection is refused.
        - socket.timeout: Logs a debug message if the connection times out.
        - Other exceptions: Logs the traceback of the exception.

    Note:
        The function ensures the socket is closed in the `finally` block to release resources.
    """
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(timeout)
        server.connect(DNS)
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        server.sendall(msg)
        return 1
    except ConnectionRefusedError:
        logger.debug(
            "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug(
            "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    finally:
        if server is not None:
            server.close()


def send_signal(DNS, msg_raw, timeout=200.0):
    """
    Sends a signal to a server using a TCP socket connection.

    This function establishes a socket connection to the specified server,
    sends a JSON-encoded message, and waits for a response. The response
    is expected to be JSON-encoded as well.

    Args:
        DNS (tuple): A tuple containing the server's host (str) and port (int).
        msg_raw (dict): The raw message to be sent, which will be JSON-encoded.
        timeout (float, optional): The timeout duration for the socket connection
            and operations, in seconds. Defaults to 200.0.

    Returns:
        dict or None: The JSON-decoded response from the server if successful,
            or None if an error occurs (e.g., connection refused, timeout, or
            other exceptions).

    Exceptions Handled:
        - ConnectionRefusedError: Logs an info message if the connection is refused.
        - socket.timeout: Logs an info message if the connection times out.
        - Other exceptions: Logs an error message with the traceback.

    Note:
        The function ensures that the socket is properly closed in the `finally` block
        to release resources.
    """
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(timeout)
        server.connect(DNS)
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        server.sendall(msg)
        returned = recvall(server).decode('utf8')
        return json.loads(returned)
    except ConnectionRefusedError:
        logger.info(
            "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.info("Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.error(str(traceback.format_exc()))
        return None
    finally:
        if server is not None:
            server.close()


def send_signal_with_conn(conn, msg_raw, only_debug=False):
    """
    Sends a signal/message through a socket connection.

    This function serializes the given message, prefixes it with its length, 
    and sends it through the provided socket connection. It handles various 
    exceptions that may occur during the process and logs appropriate messages.

    Args:
        conn (socket.socket): The socket connection object to send the message through.
        msg_raw (dict): The raw message to be sent, which will be serialized to JSON.
        only_debug (bool, optional): If True, logs messages at the debug level. 
                                     If False, logs messages at the error level. Defaults to False.

    Returns:
        int: Returns 1 if the message is sent successfully.
        None: Returns None if an exception occurs during the process.

    Exceptions Handled:
        - ConnectionRefusedError: Raised when the connection is refused.
        - socket.timeout: Raised when the socket operation times out.
        - Other exceptions: Catches all other exceptions and logs the traceback.

    Logging:
        Logs messages with details about the host and port (from the global DNS variable) 
        or the exception traceback, depending on the exception and the `only_debug` flag.
    """
    try:
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        conn.sendall(msg)
        return 1
    except ConnectionRefusedError:
        if only_debug:
            logger.debug(
                "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        else:
            logger.error(
                "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        if only_debug:
            logger.debug(
                "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        else:
            logger.error(
                "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return None


def recvall(sock):
    """
    Receives a complete message from a socket by first reading the message length
    and then reading the message content based on the length.

    Args:
        sock (socket.socket): The socket object from which to receive the message.

    Returns:
        bytes or None: The complete message received as bytes, or None if an error occurs
        or the connection is refused/timed out.

    Exceptions Handled:
        - ConnectionRefusedError: Logs a debug message if the socket connection is refused.
        - socket.timeout: Logs a debug message if the socket operation times out.
        - Any other exception: Logs the traceback of the exception.

    Notes:
        - The function assumes the message length is sent as a 4-byte big-endian integer.
        - Uses the helper function `recvall_with_given_len` to read a specific number of bytes.
        - Relies on the global variables `DNS` and `logger` for logging and host/port information.
    """
    try:
        raw_msglen = recvall_with_given_len(sock, 4)
        if not raw_msglen:
            return None
        if sys.version_info[0] == 2:
            raw_msglen = str(raw_msglen)
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall_with_given_len(sock, msglen)
    except ConnectionRefusedError:
        logger.debug(
            "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug(
            "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None


def recvall_with_given_len(sock, n):
    """
    Receives a specified number of bytes from a socket.

    This function attempts to receive exactly `n` bytes of data from the given
    socket. It continues to receive data until the desired length is achieved
    or an error occurs. If the connection is refused, times out, or any other
    exception occurs, the function logs the error and returns `None`.

    Args:
        sock (socket.socket): The socket object from which to receive data.
        n (int): The number of bytes to receive.

    Returns:
        bytes: A `bytearray` containing the received data if successful.
        None: If the connection is refused, times out, or any other error occurs.

    Exceptions Handled:
        - ConnectionRefusedError: Logs the error and returns `None` if the connection is refused.
        - socket.timeout: Logs the error and returns `None` if the socket operation times out.
        - Any other exception: Logs the traceback and returns `None`.

    Note:
        Ensure that the socket is connected and properly configured before
        calling this function. The function assumes that the socket is in a
        valid state for receiving data.
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
            "Socket connection refused : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except socket.timeout:
        logger.debug(
            "Socket timeout : host={}, port={}".format(DNS[0], DNS[1]))
        return None
    except:
        logger.debug(str(traceback.format_exc()))
        return None
    return data
