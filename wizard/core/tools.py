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
This module provides a collection of utility functions for various tasks, 
including file and directory operations, time conversions, string encryption, 
and process management. The functions are designed to simplify common 
operations and ensure safe handling of files, directories, and strings.

Key Features:
- File and directory management: Create, remove, copy, and archive files and directories.
- Time utilities: Convert timestamps, calculate time differences, and format durations.
- String utilities: Encrypt and verify strings, validate input safety.
- Process management: Wait for child processes to complete.
- Temporary file and directory creation: Generate temporary files and directories for use in scripts.

Dependencies:
- Python standard libraries: os, re, time, datetime, hashlib, binascii, shutil, tempfile, logging, traceback.
- External library: psutil (for process management).
- Wizard-specific modules: path_utils (for path handling and file operations).

Note:
- Logging is used extensively to provide feedback on operations and errors.
- Functions are designed to handle exceptions gracefully and log appropriate messages.
"""

# Python modules
from zipfile import ZipFile
import hashlib
import binascii
import os
import re
import traceback
import shutil
import tempfile
import time
import datetime
import logging
import psutil

# Wizard modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)


def natural_sort(l):
    """
    Sorts a list of strings in natural order, where numeric substrings are 
    compared based on their numeric value rather than lexicographically.

    Args:
        l (list): A list of strings to be sorted.

    Returns:
        list: A new list sorted in natural order.

    Example:
        >>> natural_sort(["item20", "item3", "item1"])
        ['item1', 'item3', 'item20']

    Note:
        This function uses regular expressions to split strings into 
        alphanumeric components for comparison.
    """
    def convert(text): return int(text) if text.isdigit() else text.lower()
    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def flushed_input(placeholder):
    """
    Prompts the user for input with a given placeholder text.

    Args:
        placeholder (str): The text to display as a prompt for the user.

    Returns:
        str: The input entered by the user.
    """
    user_input = input(placeholder)
    return user_input


def convert_time(time_float):
    """
    Converts a given time in seconds since the epoch to a formatted date and time.

    Args:
        time_float (float): The time in seconds since the epoch.

    Returns:
        tuple: A tuple containing the formatted date (YYYY-MM-DD) and time (HH:MM).

    Example:
        >>> convert_time(1633072800)
        ('2021-10-01', '00:00')
    """
    day = time.strftime('%Y-%m-%d', time.localtime(time_float))
    hour = time.strftime('%H:%M', time.localtime(time_float))
    return day, hour


def get_month(time_float):
    """
    Convert a Unix timestamp to a month abbreviation.

    Args:
        time_float (float): The Unix timestamp to be converted.

    Returns:
        str: The abbreviated month name (e.g., 'Jan', 'Feb', 'Mar').
    """
    return datetime.datetime.fromtimestamp(time_float).strftime('%b')


def get_day(time_float):
    """
    Convert a given time in seconds since the epoch (as a float) to the day of the month.

    Args:
        time_float (float): The time in seconds since the epoch.

    Returns:
        str: The day of the month as a zero-padded string (e.g., '01', '15', '31').
    """
    return time.strftime('%d', time.localtime(time_float))


def get_time_float_from_string_date(date_string, no_warning=False):
    """
    Converts a date string in the format 'day/month/year' into a Unix timestamp (float).

    Args:
        date_string (str): The date string to be converted, formatted as 'day/month/year'.
        no_warning (bool, optional): If True, suppresses warning messages for invalid date formats. Defaults to False.

    Returns:
        float: The Unix timestamp representation of the given date.
        None: If the date string is invalid and `no_warning` is True, or if an exception occurs.

    Raises:
        None: All exceptions are caught and handled internally.

    Logs:
        Logs a warning message if the date string is invalid and `no_warning` is False.
    """
    try:
        time_tokens = date_string.split('/')
        day = int(time_tokens[0])
        month = int(time_tokens[1])
        year = int(time_tokens[2])
        dt = datetime.datetime(year=year, month=month, day=day)
        time_float = time.mktime(dt.timetuple())
        return time_float
    except:
        if no_warning:
            return
        logger.warning(
            f"{date_string} not a valid date format\nPlease enter a date like following 'day/month/year'")
        return


def time_ago_from_timestamp(timestamp):
    """
    Calculate the time difference between the current UTC time and a given timestamp,
    and return a human-readable string representing the time elapsed.
    Args:
        timestamp (float): The timestamp to compare, in seconds since the epoch (UTC).
    Returns:
        str: A string representing the time elapsed, such as "2 days ago", "3 hours ago",
             "5 minutes ago", or "Now" if the timestamp is in the future or very recent.
    Notes:
        - If the time difference is more than 6 days, the result is expressed in weeks.
        - If the time difference is negative (timestamp is in the future), "Now" is returned.
    """
    now = datetime.datetime.utcfromtimestamp(time.time())
    timestamp_datetime = datetime.datetime.utcfromtimestamp(timestamp)

    time_diff = now - timestamp_datetime
    days = time_diff.days
    seconds = time_diff.seconds

    if time_diff < datetime.timedelta(0):
        return "Now"

    if days > 6:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} ago"
    elif seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} ago"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} ago"
    else:
        return f"{seconds} second{'s' if seconds > 1 else ''} ago"


def time_left_from_timestamp(timestamp):
    """
    Calculate the time remaining from the given timestamp to the current UTC time.
    Args:
        timestamp (float): The target timestamp in seconds since the epoch (UTC).
    Returns:
        str: A human-readable string representing the time left. The output can be:
            - "0 seconds left" if the timestamp is in the past.
            - "{n} weeks left" if the time left is more than 6 days.
            - "{n} days left" if the time left is between 1 and 6 days.
            - "{n} hours left" if the time left is between 1 hour and less than a day.
            - "{n} minutes left" if the time left is between 1 minute and less than an hour.
            - "{n} seconds left" if the time left is less than a minute.
    """
    now = datetime.datetime.utcfromtimestamp(time.time())
    timestamp_datetime = datetime.datetime.utcfromtimestamp(timestamp)

    time_diff = timestamp_datetime - now
    days = time_diff.days
    seconds = time_diff.seconds

    if time_diff < datetime.timedelta(0):
        return "0 seconds left"

    if days > 6:
        weeks = days // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} left"
    elif days > 0:
        return f"{days} day{'s' if days > 1 else ''} left"
    elif seconds >= 3600:
        hours = seconds // 3600
        return f"{hours} hour{'s' if hours > 1 else ''} left"
    elif seconds >= 60:
        minutes = seconds // 60
        return f"{minutes} minute{'s' if minutes > 1 else ''} left"
    else:
        return f"{seconds} second{'s' if seconds > 1 else ''} left"


def convert_seconds(time_float):
    """
    Convert a time duration in seconds into hours, minutes, and seconds.

    Args:
        time_float (float): The time duration in seconds.

    Returns:
        tuple: A tuple containing three integers:
            - hours (int): The number of hours.
            - minutes (int): The number of minutes.
            - seconds (int): The number of seconds.
    """
    hours = int(time_float/3600)
    time_float = time_float - (hours*3600)
    minutes = int(time_float/60)
    time_float = time_float - (minutes*60)
    seconds = int(time_float)
    return hours, minutes, seconds


def convert_seconds_with_miliseconds(time_float):
    """
    Converts a time duration given in seconds (as a float) into hours, minutes, 
    seconds, and milliseconds.

    Args:
        time_float (float): The time duration in seconds.

    Returns:
        tuple: A tuple containing four integers:
            - hours (int): The number of hours.
            - minutes (int): The number of minutes.
            - seconds (int): The number of seconds.
            - milliseconds (int): The remaining milliseconds.
    """
    hours = int(time_float/3600)
    time_float = time_float - (hours*3600)
    minutes = int(time_float/60)
    time_float = time_float - (minutes*60)
    seconds = int(time_float)
    time_float = time_float - (seconds)
    miliseconds = int(time_float*100)
    return hours, minutes, seconds, miliseconds


def convert_seconds_with_days(time_float):
    """
    Converts a time duration given in seconds (as a float) into a tuple
    representing the equivalent duration in days, hours, minutes, and seconds.

    Args:
        time_float (float): The time duration in seconds.

    Returns:
        tuple: A tuple containing four integers:
            - days (int): The number of complete days.
            - hours (int): The number of complete hours (0-23).
            - minutes (int): The number of complete minutes (0-59).
            - seconds (int): The remaining seconds (0-59).
    """
    days = int(time_float/(3600*24))
    time_float = time_float - (days*3600*24)
    hours = int(time_float/3600)
    time_float = time_float - (hours*3600)
    minutes = int(time_float/60)
    time_float = time_float - (minutes*60)
    seconds = int(time_float)
    return days, hours, minutes, seconds


def convert_seconds_to_string_time(time_float):
    """
    Converts a given time in seconds (as a float) into a human-readable string format.

    The function breaks down the input time into hours, minutes, and seconds, and 
    formats it into a string based on the following conditions:
    - If hours are non-zero, the output will include hours and minutes (e.g., "2h, 30m").
    - If hours are zero but minutes are non-zero, the output will include minutes and seconds (e.g., "30m, 45s").
    - If both hours and minutes are zero, the output will include only seconds (e.g., "15s").

    Args:
        time_float (float): The time in seconds to be converted.

    Returns:
        str: A human-readable string representation of the time.
    """
    hours, minutes, seconds = convert_seconds(time_float)
    if int(hours) != 0:
        string_time = f"{hours}h, {minutes}m"
    if int(minutes) != 0 and int(hours) == 0:
        string_time = f"{minutes}m, {seconds}s"
    if int(minutes) == 0 and int(hours) == 0:
        string_time = f"{seconds}s"
    return string_time


def convert_seconds_to_string_time_with_days(time_float):
    """
    Converts a given time in seconds (as a float) into a human-readable string format
    that includes days, hours, minutes, and seconds.

    The function determines the appropriate time units to display based on the input
    and omits units with a value of zero for brevity. For example:
    - If the input corresponds to multiple days, the output will include days, hours, and minutes.
    - If the input corresponds to only hours and minutes, the output will exclude days.

    Args:
        time_float (float): The time duration in seconds.

    Returns:
        str: A human-readable string representation of the time duration.
             Examples:
             - "2 days, 5h, 30m"
             - "5h, 30m"
             - "30m, 45s"
             - "15s"
    """
    days, hours, minutes, seconds = convert_seconds_with_days(time_float)
    if int(days) != 0:
        string_time = f"{days} days, {hours}h, {minutes}m"
        return string_time
    if int(hours) != 0:
        string_time = f"{hours}h, {minutes}m"
        return string_time
    if int(minutes) != 0:
        string_time = f"{minutes}m, {seconds}s"
        return string_time
    if int(minutes) == 0:
        string_time = f"{seconds}s"
        return string_time


def encrypt_string(string):
    """
    Encrypts a given string using a combination of a randomly generated salt 
    and the PBKDF2-HMAC-SHA512 algorithm.

    Args:
        string (str): The input string to be encrypted.

    Returns:
        str: The encrypted string, which is a combination of the salt and 
             the hashed password in hexadecimal format.
    """
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', string.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def decrypt_string(stored_string, provided_string):
    """
    Verifies if a provided string matches a stored, hashed string.

    This function extracts the salt from the stored string, hashes the provided
    string using the same salt and hashing algorithm, and compares the result
    with the stored hash.

    Args:
        stored_string (str): The concatenated salt and hashed string. The first
                             64 characters represent the salt, and the rest is
                             the hashed string.
        provided_string (str): The plain text string to verify.

    Returns:
        bool: True if the provided string matches the stored hash, False otherwise.
    """
    salt = stored_string[:64]
    stored_string = stored_string[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_string.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_string


def is_safe(input_string):
    """
    Checks if the given input string is safe based on specific criteria.

    A string is considered safe if:
    - It is not empty.
    - It contains only alphanumeric characters, dots (.), or underscores (_).
    - It is not composed entirely of digits.

    Args:
        input_string (str): The string to be checked.

    Returns:
        bool: True if the string is safe, False otherwise.

    Logs:
        - Logs a warning if the input string is empty.
        - Logs a warning if the input string contains illegal characters.
        - Logs a warning if the input string is composed entirely of digits.
    """
    if input_string == '':
        logger.warning(f"No data given")
        return
    charRe = re.compile(r'[^a-zA-Z0-9._]')
    string = charRe.search(input_string)
    success = not bool(string)
    if not success:
        logger.warning(f"'{input_string}' contains illegal characters")
    try:
        int(input_string)
        logger.warning(f"'{input_string}' can't only be digits")
        success = False
        print(int(input_string))
    except:
        pass
    return success


def is_dbname_safe(input_string):
    """
    Checks if the given input string is safe to use as a database name.

    A safe database name contains only lowercase letters (a-z), digits (0-9),
    and underscores (_). If the input string contains any other characters,
    it is considered unsafe.

    Args:
        input_string (str): The string to validate as a safe database name.

    Returns:
        bool: True if the input string is safe, False otherwise.
    """
    charRe = re.compile(r'[^a-z0-9_]')
    string = charRe.search(input_string)
    return not bool(string)


def zip_files(files_list, destination):
    """
    Compresses a list of files into a ZIP archive.

    Args:
        files_list (list): A list of file paths to be added to the ZIP archive.
        destination (str): The file path for the resulting ZIP archive.

    Returns:
        int: Returns 1 if the operation is successful.
        None: Returns None if an exception occurs.

    Logs:
        Logs an informational message if the files are successfully archived.
        Logs an error message with the traceback if an exception occurs.
    """
    try:
        with ZipFile(destination, 'a') as zip:
            for file in files_list:
                zip.write(file, os.path.split(file)[-1])
        logger.info("Files archived")
        return 1
    except:
        logger.error(str(traceback.format_exc()))
        return


def make_archive(source):
    """
    Creates a ZIP archive of the specified folder.

    Args:
        source (str): The path to the folder to be archived.

    Returns:
        str: The full path to the created archive file if successful.
        None: If an error occurs during the archiving process.

    Logs:
        - Logs an informational message when the folder is successfully archived.
        - Logs an error message with the traceback if an exception occurs.

    Notes:
        - The archive file is named based on the folder name with "_archive.zip" appended.
        - The archive is created in the same directory as the source folder.
    """
    try:
        format = 'zip'
        root_dir = path_utils.dirname(source)
        base_dir = os.path.basename(source.strip(os.sep))
        base_name = get_filename_without_override(path_utils.join(root_dir,
                                                                  f"{base_dir}_archive.zip"))
        shutil.make_archive(os.path.splitext(base_name)[0],
                            format,
                            root_dir,
                            base_dir)
        logger.info(f"Folder {base_dir} archived in {base_name}")
        return base_name
    except:
        logger.error(str(traceback.format_exc()))
        return


def get_filename_without_override(file):
    """
    Generates a unique filename by appending an incremental index to the base filename
    if a file with the same name already exists in the specified directory.

    Args:
        file (str): The full path of the file, including its name and extension.

    Returns:
        str: A unique file path where no file with the same name exists.

    Notes:
        - The function checks for file existence using `path_utils.isfile`.
        - The new filename is generated by appending an underscore and an index
          (e.g., "filename_1.ext", "filename_2.ext") until a unique name is found.
    """
    folder = path_utils.dirname(file)
    basename = os.path.basename(file)
    extension = os.path.splitext(basename)[-1]
    filename = os.path.splitext(basename)[0]
    index = 1
    while path_utils.isfile(file):
        new_filename = "{}_{}{}".format(filename, index, extension)
        file = path_utils.join(folder, new_filename)
        index += 1
    return file


def get_files_list_size(files_list):
    """
    Calculate the total size of all files in the given list.

    Args:
        files_list (list): A list of file paths as strings.

    Returns:
        int: The total size of all files in bytes.

    Raises:
        FileNotFoundError: If any file in the list does not exist.
        OSError: If there is an issue accessing a file's size.
    """
    total_size = 0
    for file in files_list:
        total_size += os.path.getsize(file)
    return total_size


def copy_files(files_list, destination):
    """
    Copies a list of files to a specified destination directory, ensuring no file is overwritten.

    Args:
        files_list (list): A list of file paths to be copied.
        destination (str): The directory where the files should be copied.

    Returns:
        list: A list of successfully copied file paths. If the copy operation fails, returns an empty list.

    Logs:
        - Warnings if a file in the list does not exist or if the destination directory does not exist.
        - Information about the success or failure of each file copy operation.

    Notes:
        - The function checks the existence of each file in the input list and the destination directory before proceeding.
        - Files are copied with unique names to avoid overwriting existing files in the destination directory.
        - Uses `get_filename_without_override` to generate unique file names in the destination.
    """
    sanity = 1
    for file in files_list:
        if not path_utils.isfile(file):
            sanity = 0
            logger.warning(f"{file} doesn't exists")
    if not path_utils.isdir(destination):
        logger.warning(f"{destination} doesn't exists")
        sanity = 0
    if not sanity:
        logger.warning("Can't execute copy")
        return
    new_files = []
    for file in files_list:
        file_name = os.path.split(file)[-1]
        destination_file = get_filename_without_override(path_utils.join(destination,
                                                                         file_name))
        path_utils.copyfile(file, destination_file)
        new_files.append(destination_file)
    valid_files = []
    for file in new_files:
        if os.path.isfile(file):
            logger.info(f"{destination_file} copied")
            valid_files.append(file)
        else:
            logger.info(f"Can't copy {destination_file}")
    return valid_files


def temp_dir():
    """
    Creates a temporary directory and returns its cleaned path.

    This function uses the `tempfile.mkdtemp` method to create a temporary 
    directory and then cleans the resulting path using `path_utils.clean_path`.

    Returns:
        str: The cleaned path of the created temporary directory.
    """
    tempdir = tempfile.mkdtemp()
    return path_utils.clean_path(tempdir)


def temp_dir_in_dir(directory):
    """
    Creates a temporary directory inside the specified directory.

    Args:
        directory (str): The path to the directory where the temporary directory will be created.

    Returns:
        str: The cleaned path of the created temporary directory.

    Notes:
        This function uses `tempfile.mkdtemp` to create the temporary directory
        and `path_utils.clean_path` to clean the resulting path.
    """
    tempdir = tempfile.mkdtemp(dir=directory)
    return path_utils.clean_path(tempdir)


def create_folder(dir_name):
    """
    Creates a folder with the specified directory name.

    Args:
        dir_name (str): The name of the directory to create.

    Returns:
        int: Returns 1 if the folder is successfully created.
        None: Returns None if an error occurs during folder creation.

    Logs:
        - Logs an info message if the folder is successfully created.
        - Logs an error message if the folder does not exist, already exists, or access is denied.

    Exceptions:
        - FileNotFoundError: Raised if the specified directory path does not exist.
        - FileExistsError: Raised if the directory already exists.
        - PermissionError: Raised if there is no permission to create the directory.
    """
    try:
        path_utils.mkdir(dir_name)
        logger.info(f'{dir_name} created')
        return 1
    except FileNotFoundError:
        logger.error(f"{dir_name} doesn't exists")
        return
    except FileExistsError:
        logger.error(f"{dir_name} already exists on filesystem")
        return
    except PermissionError:
        logger.error(f"{dir_name} access denied")
        return


def create_folder_if_not_exist(dir_name):
    """
    Creates a folder with the specified directory name if it does not already exist.

    Args:
        dir_name (str): The name of the directory to create.

    Returns:
        int: Returns 1 if the folder is successfully created.
        None: Returns None if an error occurs during folder creation.

    Logs:
        - Logs a debug message if the folder is successfully created.
        - Logs an error message if the folder does not exist, already exists, or access is denied.

    Exceptions:
        - FileNotFoundError: Raised if the specified directory path does not exist.
        - FileExistsError: Raised if the directory already exists.
        - PermissionError: Raised if there is no permission to create the directory.
    """
    try:
        path_utils.mkdir(dir_name)
        logger.debug(f'{dir_name} created')
        return 1
    except FileNotFoundError:
        logger.error(f"{dir_name} doesn't exists")
        return
    except FileExistsError:
        logger.error(f"{dir_name} already exists on filesystem")
        return
    except PermissionError:
        logger.error(f"{dir_name} access denied")
        return


def remove_folder(dir_name):
    """
    Removes the specified folder.

    Args:
        dir_name (str): The path of the directory to be removed.

    Returns:
        int: Returns 1 if the folder is successfully removed.
        None: Returns None if the folder does not exist or access is denied.

    Logs:
        Logs an info message if the folder is successfully removed.
        Logs an error message if the folder does not exist or access is denied.

    Exceptions:
        FileNotFoundError: Raised if the folder does not exist.
        PermissionError: Raised if access to the folder is denied.
    """
    try:
        path_utils.rmdir(dir_name)
        logger.info(f'{dir_name} removed')
        return 1
    except FileNotFoundError:
        logger.error(f"{path_utils.dirname(dir_name)} doesn't exists")
        return
    except PermissionError:
        logger.error(f"{dir_name} access denied")
        return


def remove_tree(dir_name):
    """
    Removes a directory tree at the specified path.

    Args:
        dir_name (str): The path of the directory to be removed.

    Returns:
        int: Returns 1 if the directory is successfully removed.
        None: Returns None if the directory does not exist or if access is denied.

    Logs:
        - Logs an info message if the directory is successfully removed.
        - Logs an error message if the directory does not exist.
        - Logs an error message if access to the directory is denied.
    """
    try:
        path_utils.rmtree(dir_name)
        logger.info(f'{dir_name} removed')
        return 1
    except FileNotFoundError:
        logger.error(f"{path_utils.dirname(dir_name)} doesn't exists")
        return
    except PermissionError:
        logger.error(f"{dir_name} access denied")
        return


def remove_files(files):
    """
    Removes a list of files from the filesystem.

    Args:
        files (list): A list of file paths to be removed.

    Returns:
        None

    Logs:
        - Logs an info message for each file successfully removed.
        - Logs an error message if a file does not exist or access is denied.

    Notes:
        - This function uses the `remove_file` function to handle individual file removal.
    """
    for file in files:
        remove_file(file)


def remove_file(file):
    """
    Removes the specified file from the filesystem.

    Args:
        file (str): The path to the file to be removed.

    Returns:
        int: Returns 1 if the file is successfully deleted.
        None: Returns None if the file does not exist or access is denied.

    Logs:
        Logs an informational message if the file is successfully deleted.
        Logs an error message if the file does not exist or if access is denied.

    Exceptions:
        Handles FileNotFoundError if the file does not exist.
        Handles PermissionError if access to the file is denied.
    """
    try:
        path_utils.remove(file)
        logger.info(f'{file} deleted')
        return 1
    except FileNotFoundError:
        logger.error(f"{path_utils.dirname(file)} doesn't exists")
        return
    except PermissionError:
        logger.error(f"{file} access denied")
        return


def temp_file_from_pycmd(pycmd):
    """
    Creates a temporary Python file from the given Python command string.

    This function generates a temporary directory, writes the provided Python 
    command string (`pycmd`) into a file named 'wizard_temp_script.py' within 
    that directory, and returns the cleaned path to the temporary file.

    Args:
        pycmd (str): The Python command string to be written into the temporary file.

    Returns:
        str: The cleaned path to the temporary Python file.

    Note:
        The caller is responsible for cleaning up the temporary directory and file 
        after use to avoid leaving unused temporary files on the filesystem.
    """
    tempdir = path_utils.clean_path(tempfile.mkdtemp())
    temporary_python_file = path_utils.join(tempdir, 'wizard_temp_script.py')
    with open(temporary_python_file, 'w') as f:
        f.write(pycmd)
    return path_utils.clean_path(temporary_python_file)


def shared_temp_file_from_pycmd(pycmd, directory):
    """
    Creates a temporary Python file with the given Python command string and returns its cleaned file path.

    Args:
        pycmd (str): The Python command or script content to write into the temporary file.
        directory (str): The directory where the temporary file will be created.

    Returns:
        str: The cleaned file path of the created temporary Python file.

    Notes:
        - The temporary file is created with a `.py` suffix.
        - The file path is cleaned using `path_utils.clean_path` to ensure consistency.
    """
    dunno, temporary_python_file = tempfile.mkstemp(
        suffix='.py', dir=directory)
    with open(temporary_python_file, 'w') as f:
        f.write(pycmd)
    return path_utils.clean_path(temporary_python_file)


def wait_for_child_processes():
    """
    Waits for all child processes of the current process to finish execution.

    This function retrieves all child processes of the current process and 
    continuously checks their statuses. If any child process is still running, 
    it logs the PID of the process and waits for one second before checking again. 
    The function exits once all child processes have completed.

    Note:
        - This function uses the `psutil` library to monitor process statuses.
        - It logs information about running child processes using the `logger`.

    Raises:
        psutil.NoSuchProcess: This exception is handled internally when a child 
        process no longer exists during the status check.
    """
    current_process = psutil.Process()
    children = current_process.children(recursive=True)
    while 1:
        is_running = 0
        for child in children:
            try:
                if child.status() == psutil.STATUS_RUNNING:
                    is_running = 1
                    logger.info(
                        f"Waiting for child process to end ( PID : {child.pid})")
            except psutil.NoSuchProcess:
                pass
        if is_running:
            time.sleep(1)
            continue
        else:
            break
