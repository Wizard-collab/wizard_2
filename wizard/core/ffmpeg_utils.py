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

# This module manages the project events
# the events are stored in the project database
# and are accessed by the 'project' module but
# this module decode what is stored in the
# event rows

# Python modules
import os
import subprocess
import ffmpeg
import logging
import tempfile
import cv2

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
        logger.error(
            f"Error occurred while merging videos: {e.stderr.decode('utf8')}")
    finally:
        os.remove(temp_file)


def get_temp_dir():
    tmp_dir = path_utils.join(tempfile.gettempdir(), 'wizard', 'video_manager')
    if not path_utils.isdir(tmp_dir):
        path_utils.makedirs(tmp_dir)
    return tmp_dir


def get_frames_count(video_file):
    cap = cv2.VideoCapture(video_file)
    return cap.get(cv2.CAP_PROP_FRAME_COUNT)


def extract_first_frame(video_file, temp_dir):
    cap = cv2.VideoCapture(video_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)/2))
    ret, frame = cap.read()
    destination_file = path_utils.join(
        temp_dir, f"{path_utils.basename(video_file)}.png")
    cv2.imwrite(destination_file, frame)
    return destination_file


def get_concat_video_file(temp_dir, player_id):
    return path_utils.join(temp_dir, f'{player_id}.mp4')


def concatenate_videos(temp_dir, player_id, videos_dic, fps=24):
    concat_txt_file = path_utils.join(temp_dir, f'{player_id}.txt')
    files = []
    with open(concat_txt_file, 'w') as file:
        for video in videos_dic.keys():
            file.write(f"file '{videos_dic[video]['original_file']}'\n")
            file.write(f"inpoint {videos_dic[video]['inpoint']/fps}\n")
            file.write(f"outpoint {videos_dic[video]['outpoint']/fps}\n")
            files.append(videos_dic[video]['original_file'])
    if len(files) == 0:
        logger.debug("No files to concat.")
        return
    output_video_file = get_concat_video_file(temp_dir, player_id)
    command = f"ffmpeg -y -f concat -safe 0 -i {concat_txt_file} -preset ultrafast -c copy -an -r {fps} {output_video_file}"
    res = subprocess.run(command, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)
    return output_video_file
