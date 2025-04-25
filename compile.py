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
This module provides a `compile` class that automates the process of building and packaging a software project.
It handles versioning, compilation, and packaging tasks based on the specified release type.

The module includes the following functionalities:
- Version management: Updates version information in a YAML file and generates release names.
- Compilation: Uses PyInstaller to compile project components and organize build artifacts.
- Packaging: Creates a zip archive and an installer executable for the project.
- Cleanup: Removes temporary files, folders, and `__pycache__` directories to ensure a clean build environment.

Classes:
    compile: Automates the build and packaging process for a software project.

Usage:
    Run this script with a release type argument (e.g., 'MAJOR', 'MINOR', 'PATCH', etc.) to start the build process.
"""

# Python modules
import subprocess
import os
import shutil
import time
import yaml
import sys
import logging
logger = logging.getLogger(__name__)


class compile():
    """
    The `compile` class automates the process of building and packaging a software project. 
    It handles versioning, compilation, and packaging tasks based on the specified release type.
    Attributes:
        release_type (str): The type of release to build (e.g., 'MAJOR', 'MINOR', 'PATCH', 'BUILD', etc.).
    Methods:
        __init__():
            Initializes the `compile` class, processes command-line arguments, and starts the build process.
        get_release_name():
            Determines the release name and version based on the release type. Updates version information
            in a YAML file and prepares the build folder.
        compile():
            Executes the compilation process using PyInstaller, organizes build artifacts, creates a zip archive,
            and generates an installer executable.
        clean_pycache():
            Recursively removes all `__pycache__` directories from the project to ensure a clean build environment.
    """

    def __init__(self):
        args = sys.argv
        args.pop(0)
        if len(args) >= 1:
            self.release_type = args.pop(0)
        else:
            self.release_type = None
        self.build_folder = None
        self.get_release_name()
        self.compile()

    def get_release_name(self):
        """
        Generates a release name based on the release type and updates the versioning information.
        This function manages versioning by incrementing the appropriate version component
        (MAJOR, MINOR, PATCH) based on the provided release type. It also handles the creation
        of necessary directories and files, such as `compile` and `ressources/version.yaml`, 
        to store versioning data. The release name and build folder are updated accordingly.
        Release types:
            - 'MAJOR': Increments the MAJOR version, resets MINOR and PATCH to 0.
            - 'MINOR': Increments the MINOR version, resets PATCH to 0.
            - 'PATCH': Increments the PATCH version.
            - 'REBUILD': Keeps the version unchanged.
            - 'BUILD': Keeps the version unchanged but increments the build number.
        If the release type is invalid or not provided, an error is logged.
        Attributes:
            self.release_type (str): The type of release (e.g., 'MAJOR', 'MINOR', 'PATCH', etc.).
            self.build_folder (str): The folder path for the current build.
            self.setup_name (str): The name of the setup executable for the release.
        Side Effects:
            - Creates the `compile` directory if it does not exist.
            - Creates or updates the `ressources/version.yaml` file with versioning data.
            - Logs the release name and build number.
        Raises:
            Logs an error if the release type is invalid or not provided.
        """
        if self.release_type is not None:
            # Ensure the compile directory exists
            compil_dir = 'compile'
            if not os.path.isdir(compil_dir):
                os.mkdir(compil_dir)

            # Ensure the versioning YAML file exists and initialize it if necessary
            compil_data_file = 'ressources/version.yaml'
            if not os.path.isfile(compil_data_file):
                compil_data_dic = dict()
                compil_data_dic['builds'] = 0
                # version name : MAJOR.MINOR.PATCH
                compil_data_dic['MAJOR'] = 2
                compil_data_dic['MINOR'] = 0
                compil_data_dic['PATCH'] = 0
                with open(compil_data_file, 'w') as f:
                    yaml.dump(compil_data_dic, f)
            else:
                with open(compil_data_file, 'r') as f:
                    compil_data_dic = yaml.load(f, Loader=yaml.Loader)

            # Retrieve and update versioning information
            build_no = compil_data_dic['builds']
            if self.release_type != 'BUILD':
                build_no += 1
            MAJOR = compil_data_dic['MAJOR']
            MINOR = compil_data_dic['MINOR']
            PATCH = compil_data_dic['PATCH']

            # Update version components based on the release type
            if self.release_type == 'MAJOR':
                MAJOR += 1
                MINOR = 0
                PATCH = 0
            elif self.release_type == 'MINOR':
                MINOR += 1
                PATCH = 0
            elif self.release_type == 'PATCH':
                PATCH += 1
            elif self.release_type == 'REBUILD':
                pass
            elif self.release_type == 'BUILD':
                pass
            else:
                # Log an error if the release type is invalid
                logger.error(
                    f"{self.release_type} is not a valid release type")
                MAJOR = None
                MINOR = None
                PATCH = None

            # Generate release name and update versioning data
            if (MAJOR and MINOR and PATCH) is not None:
                release_name = f"{MAJOR}.{MINOR}.{PATCH}"
                self.build_folder = os.path.join(
                    compil_dir, f"{release_name}_{str(build_no).zfill(4)}")
                self.setup_name = f'{release_name}.{str(build_no).zfill(4)}-setup.exe'
                compil_data_dic['MAJOR'] = MAJOR
                compil_data_dic['MINOR'] = MINOR
                compil_data_dic['PATCH'] = PATCH
                compil_data_dic['builds'] = build_no
                compil_data_dic['BUILDS'] = build_no
                compil_data_dic['date'] = time.time()
                compil_data_dic['setup_name'] = self.setup_name

                # Save updated versioning data to the YAML file
                with open(compil_data_file, 'w') as f:
                    yaml.dump(compil_data_dic, f)

                # Log the release name and build number
                logger.info(f"Release name : {release_name}")
                logger.info(f"Build : {build_no}")
        else:
            # Log an error if no release type is provided
            logger.error(f"please provide a release type")

    def compile(self):
        """
        Handles the compilation and packaging process for the project.

        This method performs the following steps:
        1. Cleans up any existing `__pycache__` directories and temporary build folders.
        2. Executes multiple PyInstaller commands to compile various project components.
        3. Copies necessary folders and files into the distribution folder.
        4. Creates a zip archive of the compiled project.
        5. Generates an installer executable for the project.
        6. Cleans up temporary files and folders after the process is complete.

        Attributes:
            self.build_folder (str): The folder path for the current build.
            self.setup_name (str): The name of the setup executable for the release.

        Side Effects:
            - Deletes existing `dist` and `build` directories.
            - Executes PyInstaller commands to compile project components.
            - Copies files and folders to the distribution folder.
            - Creates a zip archive and installer executable.
            - Deletes temporary files and folders after completion.
        """
        if self.build_folder is not None:
            # Clean up any existing __pycache__ directories
            self.clean_pycache()

            # Remove existing dist and build directories if they exist
            if os.path.isdir('dist'):
                shutil.rmtree('dist')
            if os.path.isdir('build'):
                shutil.rmtree('build')

            # Execute PyInstaller commands for various project components
            command_line = "PyInstaller spec/wizard.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/create_repository.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/change_repository.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/change_db_server.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/PyWizard.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/wizard_cmd.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/server.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/uninstall.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/error_handler.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            command_line = "PyInstaller spec/project_manager.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            # Copy required folders to the distribution folder
            folders_list = ['binaries', 'ressources', 'softwares']
            dist_folder = 'dist/Wizard'
            for folder in folders_list:
                destination = os.path.join(dist_folder, folder)
                shutil.copytree(folder, destination)

            # Copy required files to the distribution folder
            files_list = ['wapi.py',
                          'dist/PyWizard/PyWizard.exe',
                          'dist/Create Repository/Create Repository.exe',
                          'dist/Change Repository/Change Repository.exe',
                          'dist/Connect Server/Connect Server.exe',
                          'dist/wizard_cmd/wizard_cmd.exe',
                          'dist/server/server.exe',
                          'dist/uninstall.exe',
                          'dist/Project Manager/Project Manager.exe',
                          'dist/error_handler/error_handler.exe'
                          ]

            for file in files_list:
                destination = os.path.join(dist_folder, os.path.basename(file))
                shutil.copyfile(file, destination)

            # Copy the distribution folder to the build folder
            shutil.copytree(dist_folder, self.build_folder)

            # Clean up temporary dist and build directories
            if os.path.isdir('dist'):
                shutil.rmtree('dist')
            if os.path.isdir('build'):
                shutil.rmtree('build')

            # Create a zip archive of the build folder
            shutil.make_archive(f'{self.build_folder}',
                                'zip', self.build_folder)

            # Remove the build folder after creating the zip archive
            if os.path.isdir(self.build_folder):
                shutil.rmtree(self.build_folder)

            # Create the installer executable
            zip_file = self.build_folder + '.zip'
            shutil.copyfile(zip_file, '__wizard__.zip')

            command_line = "PyInstaller spec/installer.spec"
            p = subprocess.Popen(command_line)
            p.wait()

            # Move the installer executable to the compile directory
            shutil.copyfile('dist/__installer_temp__.exe',
                            os.path.join('compile', self.setup_name))
            os.remove('__wizard__.zip')

            # Clean up temporary dist and build directories
            if os.path.isdir('dist'):
                shutil.rmtree('dist')
            if os.path.isdir('build'):
                shutil.rmtree('build')

            # Clean up any remaining __pycache__ directories
            self.clean_pycache()

            # Open the folder containing the build
            os.startfile(os.path.dirname(self.build_folder))

    def clean_pycache(self):
        """
        Removes all `__pycache__` directories from the current working directory and its subdirectories.

        This function traverses the directory tree starting from the current working directory,
        identifies directories named `__pycache__`, logs their paths, and deletes them.

        Returns:
            None
        """
        total_chars = 0
        total_files = 0
        for root, dirs, files in os.walk(os.path.abspath(""), topdown=False):
            for directory in dirs:
                if directory == '__pycache__':
                    dir_name = os.path.join(root, directory)
                    logger.info(f"Deleting {dir_name}...")
                    shutil.rmtree(dir_name)


if __name__ == '__main__':
    compile()
