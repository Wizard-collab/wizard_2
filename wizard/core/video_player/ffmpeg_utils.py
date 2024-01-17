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
import threading
import subprocess
import cv2
import os
import logging

# Wizard core modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)

class create_proxy():
    def __init__(self, temp_dir, input_video, fps=24):
        self.temp_dir = temp_dir
        self.input_video = input_video
        self.fps = fps
        self.process = self.create_proxy()

    def create_proxy(self):
        self.proxy_file = path_utils.join(self.temp_dir, f"{path_utils.basename(self.input_video)}")
        self.temp_proxy_file = path_utils.join(self.temp_dir, f"temp_{path_utils.basename(self.input_video)}")
        if path_utils.isfile(self.proxy_file):
            return

        command = f"""ffmpeg -i {self.input_video} -vf "setpts=N/{self.fps}/TB" -codec:v libx264 -preset ultrafast -an -crf 24 -r {self.fps} {self.temp_proxy_file}"""
        process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return process

    def wait_for_process(self):
        if self.process is None:
            return
        self.process.communicate()
        self.process_finished()

    def kill(self):
        self.process.kill()

    def process_finished(self):
        if self.temp_proxy_file is None:
            return
        if self.proxy_file is None:
            return
        if not path_utils.isfile(self.temp_proxy_file):
            return
        os.rename(self.temp_proxy_file, self.proxy_file)

def clear_proxys(temp_dir):
    for file in path_utils.listdir(temp_dir):
        path_utils.remove(path_utils.join(temp_dir, file))

def concatenate_videos(temp_dir, videos_dic, fps=24):
    concat_txt_file = path_utils.join(temp_dir, 'concat.txt')
    with open(concat_txt_file, 'w') as file:
        for video in videos_dic.keys():
            proxy_video_file = path_utils.join(temp_dir, videos_dic[video]['name'])
            if not path_utils.isfile(proxy_video_file):
                logger.debug(f"{proxy_video_file} not found, replacing by black.")
                proxy_video_file = get_black_file(proxy_video_file, videos_dic[video]['frames_count'], fps)

            file.write(f"file '{path_utils.abspath(proxy_video_file)}'\n")

    output_video_file = path_utils.join(temp_dir, 'concatened.mp4')

    command = f"ffmpeg -y -f concat -safe 0 -i {concat_txt_file} -preset ultrafast -c copy -an -r {fps} {output_video_file}"
    subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return output_video_file

def get_frames_count(video_file):
    cap = cv2.VideoCapture(video_file)
    return cap.get(cv2.CAP_PROP_FRAME_COUNT)

def get_black_file(proxy_video_file, frames_count, fps):
    black_proxy_video_file = path_utils.join(path_utils.dirname(proxy_video_file), f"black_{path_utils.basename(proxy_video_file)}")
    if path_utils.isfile(black_proxy_video_file):
        if get_frames_count(black_proxy_video_file) == frames_count:
            return black_proxy_video_file
        else:
            path_utils.remove(black_proxy_video_file)
    command = f"ffmpeg -f lavfi -i color=c=black:s=19.10:r={fps} -preset ultrafast -an -t {frames_count/fps} {black_proxy_video_file}"
    subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return black_proxy_video_file