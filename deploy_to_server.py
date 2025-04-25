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
This module provides functionality to deploy compiled files and version information 
to a server. It ensures the necessary directories and files exist before copying 
the required files to their respective destinations on the server.
"""

import os
import shutil
import yaml

import logging
logger = logging.getLogger(__name__)

SERVER_DOWNLOAD_PATH = "O:/html/download/"
SERVER_CGI_BIN_PATH = "O:/html/cgi-bin/"
COMPIL_PATH = 'compile/'


def deploy_to_server():
    # Check if the server download path exists
    if not os.path.isdir(SERVER_DOWNLOAD_PATH):
        print(f"{SERVER_DOWNLOAD_PATH} not found.")
        return

    # Check if the compilation path exists
    if not os.path.isdir(COMPIL_PATH):
        print(f"{COMPIL_PATH} not found.")
        return

    # Load the version information from the YAML file
    with open("ressources/version.yaml", 'r') as f:
        build_dic = yaml.load(f, Loader=yaml.Loader)

    # Construct the path to the build file
    build_file = os.path.join(COMPIL_PATH, build_dic['setup_name'])

    # Check if the build file exists
    if not os.path.isfile(build_file):
        print(f"{build_file} not found.")
        return

    # Copy the build file to the server download path
    dest_file = os.path.join(SERVER_DOWNLOAD_PATH,
                             os.path.basename(build_file))
    print(f"Copying {build_file} to {dest_file}")
    shutil.copyfile(build_file, dest_file)

    # Verify if the build file was successfully copied
    if not os.path.isfile(dest_file):
        print(f"{dest_file} not copied")
        return

    # Copy the version.yaml file to the server CGI bin path
    yaml_dest_file = os.path.join(SERVER_CGI_BIN_PATH, "version.yaml")
    print(f"Copying version.yaml to {yaml_dest_file}")
    shutil.copyfile("ressources/version.yaml", yaml_dest_file)

    # Verify if the version.yaml file was successfully copied
    if not os.path.isfile(yaml_dest_file):
        print(f"{yaml_dest_file} not copied")
        return


if __name__ == '__main__':
    deploy_to_server()
