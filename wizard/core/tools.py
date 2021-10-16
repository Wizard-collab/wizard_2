# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
from zipfile import ZipFile
import hashlib, binascii
import os
import re
import traceback
import shutil
import tempfile
import time

# Wizard modules
from wizard.core import custom_logger
logger = custom_logger.get_logger(__name__)

def flushed_input(placeholder):
    print(placeholder+'\r')
    user_input = input()
    print(f'\r>>>{user_input}')
    return user_input

def convert_time(time_float):
    day = time.strftime('%Y-%m-%d', time.localtime(time_float))
    hour = time.strftime('%H:%M', time.localtime(time_float))
    return day, hour

def convert_seconds(time_float):
    hours = time.strftime("%H", time.gmtime(time_float))
    minutes = time.strftime("%M", time.gmtime(time_float))
    seconds = time.strftime("%S", time.gmtime(time_float))
    return hours, minutes, seconds

def convert_seconds_with_day(time_float):
    day = str(int(time.strftime("%d", time.gmtime(time_float)))-1)
    hours = str(int(time.strftime("%H", time.gmtime(time_float))))
    minutes = str(int(time.strftime("%M", time.gmtime(time_float))))
    seconds = str(int(time.strftime("%S", time.gmtime(time_float))))
    return day, hours, minutes, seconds

def convert_seconds_to_string_time(time_float):
    days, hours, minutes, seconds = convert_seconds_with_day(time_float)
    if int(days) != 0:
        string_time = f"{days}d, {hours}h"
    if int(hours) != 0 and int(days) == 0:
        string_time = f"{hours}h, {minutes}m"
    if int(minutes) != 0 and int(hours) == 0 and int(days) == 0:
        string_time = f"{minutes}m, {seconds}s"
    if int(minutes) == 0 and int(hours) == 0 and int(days) == 0:
        string_time = f"{seconds}s"
    return string_time

def encrypt_string(string):
    # Hash a string for storing.
    salt = hashlib.sha256(os.urandom(60)).hexdigest().encode('ascii')
    pwdhash = hashlib.pbkdf2_hmac('sha512', string.encode('utf-8'),
                                  salt, 100000)
    pwdhash = binascii.hexlify(pwdhash)
    return (salt + pwdhash).decode('ascii')

def decrypt_string(stored_string, provided_string):
    # Verify a stored string against one provided by user
    salt = stored_string[:64]
    stored_string = stored_string[64:]
    pwdhash = hashlib.pbkdf2_hmac('sha512',
                                  provided_string.encode('utf-8'),
                                  salt.encode('ascii'),
                                  100000)
    pwdhash = binascii.hexlify(pwdhash).decode('ascii')
    return pwdhash == stored_string

def is_safe(input):
    # Check if the given string doesn't 
    # contains illegal characters
    charRe = re.compile(r'[^a-zA-Z0-9._]')
    string = charRe.search(input)
    return not bool(string)

def zip_files(files_list, destination):
    # Create an archive with the given file list
    # No folder structure, the files are just inserted in the
    # archive
    # If the destination .zip file exists it appends 
    # the new files in it
    try:
        with ZipFile(destination, 'a') as zip:
            for file in files_list:
                zip.write(file, os.path.split(file)[-1])
        logger.info("Files archived")
        return 1
    except:
        logger.error(str(traceback.format_exc()))
        return None

def make_archive(source):
    # Create an archive of a given folder
    # /path/to/folder will become
    # /path/to/folder_archive.zip
    # The root of the archive is folder/
    try:
        format = 'zip'
        root_dir = os.path.dirname(source)
        base_dir = os.path.basename(source.strip(os.sep))
        base_name = get_filename_without_override(os.path.join(root_dir,
                                                    f"{base_dir}_archive.zip"))
        shutil.make_archive(os.path.splitext(base_name)[0],
                                                format,
                                                root_dir,
                                                base_dir)
        logger.info(f"Folder {base_dir} archived in {base_name}")
        return base_name
    except:
        logger.error(str(traceback.format_exc()))
        return None

def get_filename_without_override(file):
    # Check if a given file exists
    # While it exists, increment the filename 
    # as /path/to/filename_#.extension
    folder = os.path.dirname(file)
    basename = os.path.basename(file)
    extension = os.path.splitext(basename)[-1]
    filename = os.path.splitext(basename)[0]
    index = 1
    while os.path.isfile(file):
        new_filename = "{}_{}{}".format(filename, index, extension)
        file = os.path.join(folder, new_filename)
        index+=1
    return file

def copy_files(files_list, destination):
    # Copy the given files list to the
    # given destination folder
    # First check if the copy is possible
    # if not, return None
    sanity = 1
    for file in files_list:
        if not os.path.isfile(file):
            sanity = 0
            logger.warning(f"{file} doesn't exists")
    if not os.path.isdir(destination):
        logger.warning(f"{destination} doesn't exists")
        sanity=0
    if sanity:
        new_files = []
        for file in files_list:
            file_name = os.path.split(file)[-1]
            destination_file = get_filename_without_override(os.path.join(destination, 
                                                                            file_name))
            shutil.copyfile(file, destination_file)
            new_files.append(destination_file)
            logger.info(f"{destination_file} copied")
        return new_files
    else:
        logger.warning("Can't execute copy")
        return None

def temp_dir():
    # Return a temp directory
    tempdir = tempfile.mkdtemp()
    return tempdir

def create_folder(dir_name):
    # Tries to create a folder
    # If not possible return None and
    # log the corresponding error
    success = None
    try:
        os.mkdir(dir_name)
        logger.debug(f'{dir_name} created')
        success = 1
    except FileNotFoundError:
        logger.error(f"{os.path.dirname(dir_name)} doesn't exists")
    except FileExistsError:
        logger.error(f"{dir_name} already exists on filesystem")
    except PermissionError:
        logger.error(f"{dir_name} access denied")
    return success

def create_folder_if_not_exist(dir_name):
    # Tries to create a folder
    # If not possible return None and
    # log the corresponding error
    success = None
    try:
        if not os.path.isdir(dir_name):
            os.mkdir(dir_name)
            logger.debug(f'{dir_name} created')
            success = 1
    except FileNotFoundError:
        logger.error(f"{os.path.dirname(dir_name)} doesn't exists")
    except FileExistsError:
        logger.error(f"{dir_name} already exists on filesystem")
    except PermissionError:
        logger.error(f"{dir_name} access denied")
    return success

def remove_folder(dir_name):
    # Tries to remove a folder
    # If not possible return None and
    # log the corresponding error
    success = None
    try:
        os.rmdir(dir_name)
        logger.info(f'{dir_name} removed')
        success = 1
    except FileNotFoundError:
        logger.error(f"{os.path.dirname(dir_name)} doesn't exists")
    except PermissionError:
        logger.error(f"{dir_name} access denied")
    return success

def remove_tree(dir_name):
    # Tries to remove a folder tree
    # If not possible return None and
    # log the corresponding error
    success = None
    try:
        os.rmtree(dir_name)
        logger.info(f'{dir_name} removed')
        success = 1
    except FileNotFoundError:
        logger.error(f"{os.path.dirname(dir_name)} doesn't exists")
    except PermissionError:
        logger.error(f"{dir_name} access denied")
    return success

def temp_file_from_pycmd(pycmd):
    # return a .py temporary file 
    # from given script ( as string )
    tempdir = os.path.normpath(tempfile.mkdtemp())
    temporary_python_file = os.path.join(tempdir, 'wizard_temp_script.py')
    with open(temporary_python_file, 'w') as f:
        f.write(pycmd)
    return os.path.normpath(temporary_python_file)