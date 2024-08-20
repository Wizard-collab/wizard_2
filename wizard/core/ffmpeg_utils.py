# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# Python modules
import os
import subprocess
import ffmpeg
import logging

# Wizard core modules
from wizard.core import path_utils
from wizard.core import tools

logger = logging.getLogger(__name__)

def merge_videos(input_files, output_file):
    temp_file = path_utils.join(tools.temp_dir(), 'concat_files.txt')
    with open(temp_file, 'w') as file_list:
        for input_file in input_files:
            file_list.write(f"file '{input_file}'\n")
    try:
        (
            ffmpeg
            .input(temp_file, format='concat', safe=0)
            .output(output_file, c='copy')
            .run(overwrite_output=True)
        )
        logger.info(f"Merged video saved as {output_file}")
    except ffmpeg.Error as e:
        logger.error(f"Error occurred while merging videos: {e.stderr.decode('utf8')}")
    finally:
        os.remove(temp_file)
