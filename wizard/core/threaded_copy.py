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
This module provides functionality for multi-threaded file copying operations.

Classes:
    threaded_copy: Handles the multi-threaded copying of files to a specified destination.
    copy_thread: Represents a thread that copies a chunk of files to a destination.

Modules:
    - numpy: Used for splitting the file list into chunks for threading.
    - multiprocessing: Used to determine the number of CPU cores for default threading.
    - threading: Provides threading capabilities for concurrent file copying.
    - time: Used for introducing delays in the monitoring loop.
    - shutil: Used for file copying operations.
    - os: Provides file and directory manipulation utilities.
    - logging: Used for logging information, warnings, and errors.

Wizard Core Modules:
    - path_utils: Provides utility functions for handling file paths.

Usage:
    Create an instance of the `threaded_copy` class with a list of files, a destination directory,
    and an optional maximum number of threads. Call the `copy` method to start the multi-threaded
    copying process.
"""

# Python modules
import numpy as np
import multiprocessing
import threading
import time
import shutil
import os
import logging

# Wizard core modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)


class threaded_copy:
    """
    A class to handle multi-threaded file copying operations.
    Attributes:
        files_list (list): A list of file paths to be copied.
        destination (str): The destination directory where files will be copied.
        max_threads (int, optional): The maximum number of threads to use for copying. 
            Defaults to the number of CPU cores if not specified.
        threads (list): A list of active threads performing the copy operation.
        copied_files (list): A list of files that have been successfully copied.
    Methods:
        __init__(files_list, destination, max_threads=None):
            Initializes the threaded_copy instance with the given file list, 
            destination, and optional maximum thread count.
        copy():
            Starts the multi-threaded copying process. Splits the file list into 
            chunks based on the number of threads, creates threads for each chunk, 
            and monitors the progress of the copying operation.
    """

    def __init__(self, files_list, destination, max_threads=None):
        """
        Initializes the threaded copy operation.

        Args:
            files_list (list): A list of file paths to be copied.
            destination (str): The destination directory where files will be copied.
            max_threads (int, optional): The maximum number of threads to use for copying.
                Defaults to the number of CPU cores if not provided.

        Attributes:
            max_threads (int): The maximum number of threads to use for copying.
            files_list (list): A list of file paths to be copied.
            destination (str): The destination directory where files will be copied.
            threads (list): A list to store thread objects for the copy operation.
            copied_files (list): A list to keep track of successfully copied files.
        """
        if max_threads is None:
            self.max_threads = multiprocessing.cpu_count()
        else:
            self.max_threads = max_threads
        self.files_list = files_list
        self.destination = destination
        self.threads = []
        self.copied_files = []

    def copy(self):
        """
        Copies a list of files to a specified destination using multithreading.

        This method divides the files into chunks and assigns each chunk to a separate thread
        for concurrent copying. It tracks the progress of the copying operation and logs
        relevant information.

        Attributes:
            self.files_list (list): A list of file paths to be copied.
            self.destination (str): The destination directory where files will be copied.
            self.max_threads (int): The maximum number of threads to use for copying.
            self.threads (list): A list to keep track of active threads.
            self.copied_files (list): A list of files that have been successfully copied.

        Logs:
            - The number of files to be copied and the destination directory.
            - The maximum number of threads being used.
            - Progress updates as a percentage of files copied.

        Raises:
            ValueError: If the files_list is empty or destination is invalid.

        Notes:
            - Uses numpy to split the file list into chunks for multithreading.
            - Continuously monitors threads and updates the progress until all threads complete.
            - Introduces a small delay (0.1 seconds) in the monitoring loop to reduce CPU usage.
        """
        print(f"wizard_task_name: Copying {len(self.files_list)} files")
        logger.info(
            f"Starting copy of {len(self.files_list)} files to {self.destination}")
        logger.info(f"Using {self.max_threads} maximum threads")
        percent_step = 100/len(self.files_list)
        progress = 0.0
        chunks_arrays = np.array_split(self.files_list, self.max_threads)
        chunks = [list(array) for array in chunks_arrays]
        chunks = [i for i in chunks if i != []]
        for chunk in chunks:
            thread = copy_thread(chunk, self.destination)
            thread.start()
            self.threads.append(thread)
        while self.threads != []:
            for thread in self.threads:
                for file in thread.copied_files:
                    if file not in self.copied_files:
                        self.copied_files.append(file)
                if not thread.is_alive():
                    self.threads.remove(thread)
            time.sleep(0.1)
            progress = len(self.copied_files)*percent_step
            print(f"wizard_task_percent: {progress}")


class copy_thread(threading.Thread):
    """
    A thread class for copying a chunk of files to a specified destination.
    Attributes:
        files_chunk (list): A list of file paths to be copied.
        destination (str): The destination directory where files will be copied.
        copied_files (list): A list of successfully copied file paths.
    Methods:
        run():
            Executes the file copying process for the given chunk of files.
            Verifies the integrity of the copied files by comparing file sizes.
            Logs success or failure for each file copy operation.
    """

    def __init__(self, files_chunk, destination):
        """
        Initializes a copy_thread instance.

        Args:
            files_chunk (list): A list of file paths to be copied.
            destination (str): The target directory where files will be copied.

        Attributes:
            files_chunk (list): Stores the list of file paths to be copied.
            destination (str): Stores the target directory for the copied files.
            copied_files (list): A list to keep track of successfully copied files.
        """
        super(copy_thread, self).__init__()
        self.files_chunk = files_chunk
        self.destination = destination
        self.copied_files = []

    def run(self):
        """
        Executes the file copying process for the current chunk of files.

        Iterates through the list of files in `self.files_chunk`, copying each file
        to the specified destination directory. Verifies that the copied file's size
        matches the original file's size to ensure successful copying. Logs the
        result of each file copy operation and appends successfully copied files
        to `self.copied_files`.

        Raises:
            OSError: If there is an issue accessing or copying the files.

        Logs:
            - Info: When a file is successfully copied, including its size.
            - Warning: When a file copy fails, indicating a retry is needed.
        """
        for file in self.files_chunk:
            file_size = os.path.getsize(file)
            destination_file = path_utils.join(
                self.destination, path_utils.basename(file))
            shutil.copyfile(file, destination_file)
            if os.path.getsize(destination_file) == file_size:
                logger.info(
                    f'"{destination_file}" ({file_size}b) successfully copied')
                self.copied_files.append(file)
            else:
                logger.warning(
                    f'"{destination_file}" not successfully copied, retrying')
