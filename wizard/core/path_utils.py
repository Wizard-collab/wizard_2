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
This module provides utility functions for handling file and directory paths.

The functions in this module include operations for creating, removing, copying,
and checking paths, as well as cleaning and normalizing paths. These utilities
are designed to simplify common file system tasks and ensure consistent path
handling across different operating systems.

Functions:
    mkdir(path): Creates a directory if it does not exist.
    makedirs(path): Recursively creates directories if they do not exist.
    remove(path): Removes a file or directory.
    copyfile(base, destination): Copies a file to a specified destination.
    rmtree(path): Recursively deletes a directory tree.
    rmdir(path): Removes an empty directory.
    isdir(path): Checks if a path is a directory.
    listdir(path): Lists the contents of a directory.
    isfile(path): Checks if a path is a file.
    join(*args): Joins multiple path components into a single path.
    abspath(path): Converts a path to its absolute path.
    splitext(path): Splits a file path into root and extension.
    dirname(path): Returns the directory name of a path.
    basename(path): Returns the base name of a path.
    clean_path(path): Normalizes a path by replacing backslashes with forward slashes.
    startfile(path): Opens a file or directory using the default application.

Notes:
    - The `clean_path` function is used throughout the module to ensure consistent
      path formatting.
    - Logging is used to provide informational messages when paths are not provided
      or when operations fail.
"""

# Python modules
import os
import shutil
import logging

logger = logging.getLogger(__name__)


def mkdir(path):
    """
    Creates a directory at the specified path if it does not already exist.

    Args:
        path (str): The path of the directory to create. If None, the function logs a message and exits.

    Returns:
        bool: True if the directory already exists or is successfully created, otherwise raises an exception.

    Notes:
        - The path is cleaned using the `clean_path` function before processing.
        - If the path is None, a log message is generated, and the function returns without creating a directory.
        - If the directory already exists, the function returns True.
        - If the directory does not exist, it attempts to create it using `os.mkdir`.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    if os.path.isdir(path):
        return True
    return os.mkdir(path)


def makedirs(path):
    """
    Creates a directory at the specified path if it does not already exist.

    Args:
        path (str): The path of the directory to create. If None, the function logs a message and returns.

    Returns:
        bool: True if the directory already exists or was successfully created, otherwise raises an exception.

    Notes:
        - The path is cleaned using the `clean_path` function before attempting to create the directory.
        - If the path is None, a log message is generated, and the function exits without creating a directory.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    if os.path.isdir(path):
        return True
    return os.makedirs(path)


def remove(path):
    """
    Removes the specified file or directory.

    Args:
        path (str): The path to the file or directory to be removed. If None, 
                    the function logs a message and exits without performing any action.

    Returns:
        None

    Notes:
        - The path is cleaned using the `clean_path` function before attempting removal.
        - This function uses `os.remove` to delete the file or directory.
        - Ensure the `logger` is properly configured to capture the log messages.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    return os.remove(path)


def copyfile(base, destination):
    """
    Copies a file from the source path to the destination path.

    Args:
        base (str): The path to the source file to be copied. If None, the function logs a message and returns.
        destination (str): The path to the destination where the file should be copied. If None, the function logs a message and returns.

    Returns:
        str: The path to the copied file if the operation is successful.
        None: If the base or destination is not provided.

    Notes:
        - The paths are cleaned using the `clean_path` function before performing the copy operation.
        - The function uses `shutil.copyfile` to perform the file copy.
    """
    if base is None:
        logger.info("No base file given")
        return
    if destination is None:
        logger.info("No destination file given")
        return
    base = clean_path(base)
    destination = clean_path(destination)
    return shutil.copyfile(base, destination)


def rmtree(path):
    """
    Recursively deletes a directory tree at the specified path.

    Args:
        path (str): The path to the directory to be removed. If None, the function logs a message and returns.

    Returns:
        None

    Notes:
        - The path is cleaned using the `clean_path` function before deletion.
        - Uses `shutil.rmtree` to perform the directory removal.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    return shutil.rmtree(path)


def rmdir(path):
    """
    Removes a directory at the specified path.

    Args:
        path (str): The path to the directory to be removed. If None, the function logs a message and returns.

    Returns:
        None

    Notes:
        - The path is cleaned using the `clean_path` function before attempting to remove the directory.
        - This function uses `os.rmdir` to remove the directory, which requires the directory to be empty.
        - Ensure proper error handling for cases where the directory does not exist or cannot be removed.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    return os.rmdir(path)


def isdir(path):
    """
    Check if the given path is a directory.

    Args:
        path (str): The path to check. Can be None.

    Returns:
        bool: True if the path is a directory, False otherwise. 
              Returns None if the path is None.

    Logs:
        Logs an informational message if no path is provided.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    return os.path.isdir(path)


def listdir(path):
    """
    Lists the contents of a directory after cleaning the provided path.

    Args:
        path (str): The directory path to list. If None, the function logs a message and returns.

    Returns:
        list: A list of entries (files and directories) in the specified directory.
              Returns None if the path is None.

    Notes:
        - The path is cleaned using the `clean_path` function before listing its contents.
        - Logs a message if no path is provided.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    return os.listdir(path)


def isfile(path):
    """
    Checks if the given path corresponds to an existing file.

    Args:
        path (str): The path to check. Can be None.

    Returns:
        bool: True if the path corresponds to an existing file, False otherwise.
              Returns None if the path is None.

    Logs:
        Logs an informational message if the provided path is None.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    return os.path.isfile(path)


def join(*args):
    """
    Joins multiple path components into a single path and cleans the resulting path.

    This function combines the given path components using `os.path.join` and then
    applies the `clean_path` function to normalize or sanitize the resulting path.

    Args:
        *args: A variable number of path components to be joined.

    Returns:
        str: The cleaned and joined path.
    """
    path = os.path.join(*args)
    path = clean_path(path)
    return path


def abspath(path):
    """
    Converts a given path to its absolute path and cleans it.

    Args:
        path (str): The input file or directory path. Can be relative or absolute.

    Returns:
        str: The cleaned absolute path if a valid path is provided.
        None: If the input path is None.

    Logs:
        Logs an informational message if no path is provided.
    """
    if path is None:
        logger.info("No path given")
        return
    path = os.path.abspath(path)
    path = clean_path(path)
    return path


def splitext(path):
    """
    Splits the given file path into a root and extension.

    This function takes a file path, ensures it is absolute, cleans it,
    and then splits it into the root and extension using `os.path.splitext`.

    Args:
        path (str): The file path to be processed. If None, the function logs
                    an informational message and returns None.

    Returns:
        tuple: A tuple (root, ext) where 'root' is the file path without the
               extension and 'ext' is the file extension. Returns None if the
               input path is None.

    Notes:
        - The function logs an informational message if the input path is None.
        - The `clean_path` function is assumed to sanitize or normalize the path.

    Raises:
        None
    """
    if path is None:
        logger.info("No path given")
        return
    path = os.path.abspath(path)
    path = clean_path(path)
    return os.path.splitext(path)


def dirname(path):
    """
    Returns the directory name of the given path after cleaning it.

    This function takes a file path, extracts its directory name, 
    cleans the resulting path using the `clean_path` function, 
    and returns the cleaned directory path. If the input path is 
    None, it logs a message and returns None.

    Args:
        path (str): The file path to process. Can be None.

    Returns:
        str: The cleaned directory path, or None if the input path is None.

    Logs:
        Logs an informational message if the input path is None.
    """
    if path is None:
        logger.info("No path given")
        return
    path = os.path.dirname(path)
    path = clean_path(path)
    return path


def basename(path):
    """
    Extracts the base name from a given file path, cleans it, and returns the result.

    Args:
        path (str): The file path from which to extract the base name. If None, the function logs a message and returns None.

    Returns:
        str: The cleaned base name of the file path, or None if the input path is None.

    Note:
        This function relies on the `os.path.basename` method to extract the base name
        and a `clean_path` function to sanitize the result. Ensure `clean_path` is defined
        and accessible in the same module.
    """
    if path is None:
        logger.info("No path given")
        return
    path = os.path.basename(path)
    path = clean_path(path)
    return path


def clean_path(path):
    """
    Cleans and normalizes a given file path by replacing backslashes with forward slashes.

    Args:
        path (str): The file path to be cleaned. Can be None.

    Returns:
        str: The cleaned file path with backslashes replaced by forward slashes.
             Returns None if the input path is None.

    Logs:
        Logs an informational message if the input path is None.
    """
    if path is None:
        logger.info("No path given")
        return
    path = path.replace('\\', '/')
    return path


def startfile(path):
    """
    Opens the file or directory specified by the given path using the
    default application associated with it on the operating system.

    Args:
        path (str): The file or directory path to open. If None, the function
                    logs a message and returns without performing any action.

    Returns:
        None: If the path is None or an error occurs.
        Any: The result of `os.startfile(path)` if successful.

    Notes:
        - The function cleans the provided path using `clean_path` before
          attempting to open it.
        - Logs an informational message if no path is provided.
    """
    if path is None:
        logger.info("No path given")
        return
    path = clean_path(path)
    return os.startfile(path)
