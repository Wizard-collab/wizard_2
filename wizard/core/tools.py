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

# Wizard modules
from wizard.core import logging
logging = logging.get_logger(__name__)

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
        logging.info("Files archived")
        return 1
    except:
        logging.error(str(traceback.format_exc()))
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
        base_name = get_filename_without_override(os.path.join(root_dir, f"{base_dir}_archive.zip"))
        shutil.make_archive(os.path.splitext(base_name)[0], format, root_dir, base_dir)
        logging.info(f"Folder {base_dir} archived in {base_name}")
        return 1
    except:
        logging.error(str(traceback.format_exc()))
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
            logging.warning(f"{file} doesn't exists")
    if not os.path.isdir(destination):
        logging.warning(f"{destination} doesn't exists")
        sanity=0
    if sanity:
        new_files = []
        for file in files_list:
            file_name = os.path.split(file)[-1]
            destination_file = get_filename_without_override(os.path.join(destination, file_name))
            shutil.copyfile(file, destination_file)
            new_files.append(destination_file)
            logging.info(f"{destination_file} copied")
        return new_files
    else:
        logging.warning("Can't execute copy")
        return None

def temp_dir():
    # Return a temp directory
    tempdir = tempfile.mkdtemp()
    return tempdir

def create_folder(dir_name):
    success = None
    try:
        os.mkdir(dir_name)
        logging.info(f'{dir_name} created')
        success = 1
    except FileNotFoundError:
        logging.error(f"{os.path.dirname(dir_name)} doesn't exists")
    except FileExistsError:
        logging.error(f"{dir_name} already exists on filesystem")
    except PermissionError:
        logging.error(f"{dir_name} access denied")
    return success

def remove_folder(dir_name):
    success = None
    try:
        os.rmdir(dir_name)
        logging.info(f'{dir_name} removed')
        success = 1
    except FileNotFoundError:
        logging.error(f"{os.path.dirname(dir_name)} doesn't exists")
    except PermissionError:
        logging.error(f"{dir_name} access denied")
    return success

def remove_tree(dir_name):
    success = None
    try:
        os.rmtree(dir_name)
        logging.info(f'{dir_name} removed')
        success = 1
    except FileNotFoundError:
        logging.error(f"{os.path.dirname(dir_name)} doesn't exists")
    except PermissionError:
        logging.error(f"{dir_name} access denied")
    return success