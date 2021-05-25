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