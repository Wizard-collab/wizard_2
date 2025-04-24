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
This module provides utility functions for socket programming, including
functions to establish connections, send and receive data, and manage
server sockets. It includes error handling and logging for various
socket-related operations.

Functions:
    - get_local_ip: Retrieves the local IP address of the machine.
    - get_connection: Establishes a socket connection to a specified address.
    - get_port: Finds an available port starting from a base port.
    - get_server: Creates and returns a server socket bound to a specified address.
    - send_bottle: Sends a serialized message to a server using a TCP socket.
    - send_signal: Sends a signal to a server and waits for a response.
    - send_signal_with_conn: Sends a serialized message through a given connection.
    - recvall: Receives a complete message from a socket.
    - recvall_with_given_len: Receives a specific number of bytes from a socket.
"""

# Python modules
import socket
import json
import traceback
import struct
import logging

logger = logging.getLogger(__name__)


def get_local_ip():
    """
    Retrieves the local IP address of the machine.

    This function attempts to determine the local IP address by resolving the
    hostname of the machine. If an error occurs during the process, it logs
    the exception details.

    Returns:
        str: The local IP address of the machine, if successfully resolved.

    Logs:
        Logs an error message with the traceback if an exception occurs.
    """
    try:
        host_name = socket.gethostname()
        local_ip = socket.gethostbyname(host_name)
        return local_ip
    except:
        logger.error(str(traceback.format_exc()))


def get_connection(DNS, timeout=5.0, only_debug=False):
    """
    Establishes a socket connection to the specified DNS address and port.

    Args:
        DNS (tuple): A tuple containing the host (str) and port (int) to connect to.
        timeout (float, optional): The timeout duration in seconds for the connection. Defaults to 5.0.
        only_debug (bool, optional): If True, logs messages at the debug level; otherwise, logs at the info or error level. Defaults to False.

    Returns:
        socket.socket or None: Returns the socket connection object if successful, or None if the connection fails.

    Logs:
        - Logs a debug or info message if the connection is refused.
        - Logs a debug or info message if the connection times out.
        - Logs a debug or error message for any other exceptions.
    """
    try:
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.settimeout(timeout)
        connection.connect((DNS[0], DNS[1]))
        return connection
    except ConnectionRefusedError:
        if only_debug:
            logger.debug(
                f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        else:
            logger.info(
                f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        if only_debug:
            logger.debug(
                f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        else:
            logger.info(
                f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return


def get_port(ip_adress):
    """
    Finds and returns an available port starting from 11111.

    This function iteratively checks for an available port by attempting to 
    establish a connection starting from port 11111. If the port is already 
    in use, it increments the port number and retries until an available 
    port is found.

    Args:
        ip_adress (str): The IP address to check the port availability against. 
                         (Note: The parameter is not used in the current implementation.)

    Returns:
        int: An available port number.
    """
    port = 11111
    while get_connection(('localhost', port),
                         timeout=0.02,
                         only_debug=True):
        port += 1
    return port


def get_server(DNS):
    """
    Creates and returns a server socket bound to the specified DNS address.

    Args:
        DNS (tuple): A tuple containing the host (str) and port (int) to bind the server socket.

    Returns:
        tuple: A tuple containing:
            - server (socket.socket): The created server socket, or None if an error occurred.
            - server_address (str): The resolved server address (IP address), or None if an error occurred.

    Exceptions:
        - Logs a debug message if the connection is refused (ConnectionRefusedError).
        - Logs a debug message with the traceback if any other exception occurs.
    """
    try:
        server_address = socket.gethostbyname(DNS[0])
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind(DNS)
        server.listen(100)
        return server, server_address
    except ConnectionRefusedError:
        logger.debug(
            f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return None, None
    except:
        logger.debug(str(traceback.format_exc()))
        return None, None


def send_bottle(DNS, msg_raw, timeout=0.01):
    """
    Sends a serialized message to a specified server using a TCP socket.

    Args:
        DNS (tuple): A tuple containing the host (str) and port (int) of the server.
        msg_raw (dict): The raw message to be sent, which will be serialized to JSON.
        timeout (float, optional): The timeout duration in seconds for the socket connection. Defaults to 0.01.

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
        server.connect((DNS[0], DNS[1]))
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        server.sendall(msg)
        return 1
    except ConnectionRefusedError:
        logger.debug(
            f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        logger.debug(
            f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        logger.debug(str(traceback.format_exc()))
        return
    finally:
        if server:
            server.close()


def send_signal(DNS, msg_raw, timeout=5.0):
    """
    Sends a signal to a specified server using a socket connection.

    This function establishes a TCP connection to the server specified by the 
    DNS tuple (host, port), sends a JSON-encoded message, and waits for a response.

    Args:
        DNS (tuple): A tuple containing the server's hostname or IP address (str) 
                     and port number (int).
        msg_raw (dict): The message to be sent, represented as a dictionary. 
                        It will be serialized to JSON format.
        timeout (float, optional): The timeout duration in seconds for the socket 
                                   connection. Defaults to 5.0 seconds.

    Returns:
        dict or None: The response from the server, decoded from JSON format, 
                      or None if an error occurs or no response is received.

    Exceptions:
        Logs errors for the following cases:
        - ConnectionRefusedError: If the connection to the server is refused.
        - socket.timeout: If the connection times out.
        - Any other exceptions are logged with their traceback.

    Note:
        The function ensures the socket is properly closed in the `finally` block 
        to release resources.
    """
    server = None
    try:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.settimeout(timeout)
        server.connect((DNS[0], DNS[1]))
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        server.sendall(msg)
        returned_b = recvall(server)
        if returned_b:
            return json.loads(returned_b.decode('utf8'))
        else:
            return
    except ConnectionRefusedError:
        logger.error(
            f"Socket connection refused : host={DNS[0]}, port={DNS[1]}")
        return
    except socket.timeout:
        logger.error(
            f"Socket timeout ({str(timeout)}s) : host={DNS[0]}, port={DNS[1]}")
        return
    except:
        logger.error(str(traceback.format_exc()))
        return
    finally:
        if server:
            server.close()


def send_signal_with_conn(conn, msg_raw, only_debug=False):
    """
    Sends a serialized message through a given connection.

    This function serializes the provided message, prefixes it with its length,
    and sends it through the specified connection. If an error occurs during
    the process, it logs the exception either as a debug or error message
    depending on the `only_debug` flag.

    Args:
        conn (socket.socket): The connection object used to send the message.
        msg_raw (dict): The raw message to be serialized and sent.
        only_debug (bool, optional): If True, logs exceptions as debug messages;
                                      otherwise, logs them as error messages. Defaults to False.

    Returns:
        int: Returns 1 if the message is sent successfully.
        None: Returns None if an exception occurs.
    """
    try:
        msg = json.dumps(msg_raw).encode('utf8')
        msg = struct.pack('>I', len(msg)) + msg
        conn.sendall(msg)
        return 1
    except:
        if only_debug:
            logger.debug(str(traceback.format_exc()))
        else:
            logger.error(str(traceback.format_exc()))
        return


def recvall(sock):
    """
    Receives a complete message from a socket.

    This function reads a message from the given socket by first reading
    a fixed-length header (4 bytes) that specifies the length of the
    message. It then reads the remaining message based on the length
    specified in the header.

    Args:
        sock (socket.socket): The socket object to read data from.

    Returns:
        bytes: The complete message received from the socket, or None if
        an error occurs or the connection is closed.

    Notes:
        - The function uses a helper function `recvall_with_given_len`
          to read a specific number of bytes from the socket.
        - If an exception occurs during the process, it logs the traceback
          and returns None.
    """
    try:
        raw_msglen = recvall_with_given_len(sock, 4)
        if not raw_msglen:
            return
        msglen = struct.unpack('>I', raw_msglen)[0]
        return recvall_with_given_len(sock, msglen)
    except:
        logger.debug(str(traceback.format_exc()))
        return


def recvall_with_given_len(sock, n):
    """
    Receive a specific number of bytes from a socket.

    This function attempts to read exactly `n` bytes of data from the given socket.
    It continues reading until the desired length is achieved or the connection is closed.

    Args:
        sock (socket.socket): The socket object to receive data from.
        n (int): The number of bytes to read.

    Returns:
        bytearray: A bytearray containing the received data if successful.
        None: If the connection is closed before receiving the required number of bytes
              or if an exception occurs.

    Note:
        - If the connection is closed before `n` bytes are received, the function returns `None`.
        - Any exceptions during the operation are logged using the `logger.debug` method.
    """
    try:
        data = bytearray()
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return
            data.extend(packet)
        return data
    except:
        logger.debug(str(traceback.format_exc()))
        return
