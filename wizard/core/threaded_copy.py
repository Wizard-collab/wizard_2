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
    def __init__(self, files_list, destination, max_threads=None):
        if max_threads is None:
            self.max_threads = multiprocessing.cpu_count()
        else:
            self.max_threads = max_threads
        self.files_list = files_list
        self.destination = destination
        self.threads = []
        self.copied_files = []

    def copy(self):
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
    def __init__(self, files_chunk, destination):
        super(copy_thread, self).__init__()
        self.files_chunk = files_chunk
        self.destination = destination
        self.copied_files = []

    def run(self):
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
