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
    def convert(text): return int(text) if text.isdigit() else text.lower()
    def alphanum_key(key): return [convert(c)
                                   for c in re.split('([0-9]+)', key)]
    return sorted(l, key=alphanum_key)


def flushed_input(placeholder):
    user_input = input(placeholder)
    return user_input


def convert_time(time_float):
    day = time.strftime('%Y-%m-%d', time.localtime(time_float))
    hour = time.strftime('%H:%M', time.localtime(time_float))
    return day, hour


def get_month(time_float):
    return datetime.datetime.fromtimestamp(time_float).strftime('%b')


def get_day(time_float):
    return time.strftime('%d', time.localtime(time_float))


def get_time_float_from_string_date(date_string, no_warning=False):
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
    hours = int(time_float/3600)
    time_float = time_float - (hours*3600)
    minutes = int(time_float/60)
    time_float = time_float - (minutes*60)
    seconds = int(time_float)
    return hours, minutes, seconds


def convert_seconds_with_miliseconds(time_float):
    hours = int(time_float/3600)
    time_float = time_float - (hours*3600)
    minutes = int(time_float/60)
    time_float = time_float - (minutes*60)
    seconds = int(time_float)
    time_float = time_float - (seconds)
    miliseconds = int(time_float*100)
    return hours, minutes, seconds, miliseconds


def convert_seconds_with_days(time_float):
    days = int(time_float/(3600*24))
    time_float = time_float - (days*3600*24)
    hours = int(time_float/3600)
    time_float = time_float - (hours*3600)
    minutes = int(time_float/60)
    time_float = time_float - (minutes*60)
    seconds = int(time_float)
    return days, hours, minutes, seconds


def convert_seconds_to_string_time(time_float):
    hours, minutes, seconds = convert_seconds(time_float)
    if int(hours) != 0:
        string_time = f"{hours}h, {minutes}m"
    if int(minutes) != 0 and int(hours) == 0:
        string_time = f"{minutes}m, {seconds}s"
    if int(minutes) == 0 and int(hours) == 0:
        string_time = f"{seconds}s"
    return string_time


def convert_seconds_to_string_time_with_days(time_float):
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
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', string.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')


def decrypt_string(stored_string, provided_string):
    salt = stored_string[:64]
    stored_string = stored_string[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_string.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_string


def is_safe(input_string):
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
    charRe = re.compile(r'[^a-z0-9_]')
    string = charRe.search(input_string)
    return not bool(string)


def zip_files(files_list, destination):
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
    total_size = 0
    for file in files_list:
        total_size += os.path.getsize(file)
    return total_size


def copy_files(files_list, destination):
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
    tempdir = tempfile.mkdtemp()
    return path_utils.clean_path(tempdir)


def temp_dir_in_dir(directory):
    tempdir = tempfile.mkdtemp(dir=directory)
    return path_utils.clean_path(tempdir)


def create_folder(dir_name):
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
    for file in files:
        remove_file(file)


def remove_file(file):
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
    tempdir = path_utils.clean_path(tempfile.mkdtemp())
    temporary_python_file = path_utils.join(tempdir, 'wizard_temp_script.py')
    with open(temporary_python_file, 'w') as f:
        f.write(pycmd)
    return path_utils.clean_path(temporary_python_file)


def shared_temp_file_from_pycmd(pycmd, directory):
    dunno, temporary_python_file = tempfile.mkstemp(
        suffix='.py', dir=directory)
    with open(temporary_python_file, 'w') as f:
        f.write(pycmd)
    return path_utils.clean_path(temporary_python_file)


def wait_for_child_processes():
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
