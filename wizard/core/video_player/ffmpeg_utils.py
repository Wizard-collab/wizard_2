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
import time
import os
import logging
import tempfile
import base64

# Wizard core modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)

def get_temp_dir():
    tmp_dir = path_utils.join(tempfile.gettempdir(), 'wizard', 'video_manager')
    if not path_utils.isdir(tmp_dir):
        path_utils.makedirs(tmp_dir)
    return tmp_dir

def encode_path_to_name(input_path):
    encoded_bytes = base64.b64encode(input_path.encode('utf-8'))
    encoded_string = f"{encoded_bytes.decode('utf-8')}.mp4"
    return encoded_string

def check_if_proxy_exists(temp_dir, input_path):
    return path_utils.isfile(path_utils.join(temp_dir, encode_path_to_name(input_path)))

def check_if_thumbnail_exists(temp_dir, input_path):
    path = get_thumbnail_path(temp_dir, input_path)
    if path_utils.isfile(path):
        return path
    else:
        return

def decode_name_to_path(encoded_path):
    encoded_string = os.path.splitext(path_utils.basename(encoded_path))[0]
    decoded_bytes = base64.b64decode(encoded_string.encode('utf-8'))
    decoded_string = decoded_bytes.decode('utf-8')
    return decoded_string

def delete_proxy(temp_dir, original_file_name):
    proxy_file = path_utils.join(temp_dir, encode_path_to_name(original_file_name))
    if path_utils.isfile(proxy_file):
        path_utils.remove(proxy_file)

def clear_player_files(temp_dir, player_id):
    concat_txt_file = path_utils.join(temp_dir, f'{player_id}.txt')
    output_video_file = path_utils.join(temp_dir, f'{player_id}.mp4')
    if path_utils.isfile(concat_txt_file):
        path_utils.remove(concat_txt_file)
    if path_utils.isfile(output_video_file):
        path_utils.remove(output_video_file)

def get_thumbnail_path(temp_dir, original_video_file):
    return path_utils.join(temp_dir, encode_path_to_name(original_video_file).replace('.mp4', '.jpg'))

class create_proxy():
    def __init__(self, temp_dir, input_video, resolution=[1920,1080], fps=24):
        self.temp_dir = temp_dir
        self.input_video = input_video
        self.resolution = resolution
        self.fps = fps
        self.process = self.create_proxy()

    def create_proxy(self):
        self.proxy_file = path_utils.join(self.temp_dir, encode_path_to_name(self.input_video))
        self.thumbnail_file = path_utils.join(self.temp_dir, encode_path_to_name(self.input_video).replace('.mp4', '.jpg'))
        self.temp_proxy_file = path_utils.join(self.temp_dir, f"temp_{path_utils.basename(self.proxy_file)}")
        if path_utils.isfile(self.proxy_file):
            return

        command = f'''ffmpeg -i "{self.input_video}" -vf "setpts=N/{self.fps}/TB,scale={self.resolution[0]}:{self.resolution[1]}:force_original_aspect_ratio=decrease,pad={self.resolution[0]}:{self.resolution[1]}:-1:-1,setsar=1" -preset ultrafast -c:v libx264 -an -crf 10 -g 1 -r {self.fps} "{self.temp_proxy_file}"'''
        process = subprocess.Popen(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        return process

    def wait_for_process(self):
        if self.process is None:
            return
        self.process.communicate()

    def kill(self):
        if self.process is None:
            return
        self.process.kill()

    def process_finished(self):
        if self.temp_proxy_file is None:
            return
        if self.proxy_file is None:
            return
        if not path_utils.isfile(self.temp_proxy_file):
            return
        os.rename(self.temp_proxy_file, self.proxy_file)
        extract_first_frame(self.proxy_file, self.thumbnail_file)

def hard_clear_proxys(temp_dir):
    for file in path_utils.listdir(temp_dir):
        path_utils.remove(path_utils.join(temp_dir, file))

def concatenate_videos(temp_dir, player_id, videos_dic, fps=24):
    concat_txt_file = path_utils.join(temp_dir, f'{player_id}.txt')
    files = []
    with open(concat_txt_file, 'w') as file:
        for video in videos_dic.keys():
            proxy_video_file = path_utils.join(temp_dir, encode_path_to_name(videos_dic[video]['original_file']))
            if (not path_utils.isfile(proxy_video_file)) or (not videos_dic[video]['proxy']):
                break
            file.write(f"file '{path_utils.abspath(proxy_video_file)}'\n")
            file.write(f"inpoint {videos_dic[video]['inpoint']}\n")
            file.write(f"outpoint {videos_dic[video]['outpoint']}\n")
            files.append(path_utils.abspath(proxy_video_file))
    if len(files) == 0:
        logger.debug("No files to concat.")
        return
    output_video_file = path_utils.join(temp_dir, f'{player_id}.mp4')
    command = f"ffmpeg -y -f concat -safe 0 -i {concat_txt_file} -preset ultrafast -c copy -an -r {fps} {output_video_file}"
    res = subprocess.run(command, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return output_video_file

def get_frames_count(video_file):
    cap = cv2.VideoCapture(video_file)
    return cap.get(cv2.CAP_PROP_FRAME_COUNT)

def extract_first_frame(video_file, destination_file):
    cap = cv2.VideoCapture(video_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)/2))
    ret, frame = cap.read()
    cv2.imwrite(destination_file, frame)