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
from ffmpeg import FFmpeg
import threading
import subprocess
import logging
import cv2

# Wizard core modules
from wizard.core import path_utils

logger = logging.getLogger(__name__)

def create_proxys(temp_dir, video_files, output_framerate=24):
    threads = []
    for video_file in video_files:
        thread = threading.Thread(target=create_proxy, args=(temp_dir, video_file))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

def create_proxy(temp_dir, input_video, output_framerate=24):
    proxy_file = path_utils.join(temp_dir, input_video)
    if path_utils.isfile(proxy_file):
        return

    frames_count = get_frames_count(input_video)

    ffmpeg = (
        FFmpeg()
        .option("y")
        .input(input_video)
        .output(
            proxy_file,
            {"codec:v": "libx264"},
            preset="medium",
            crf=24,
            r=output_framerate,
            acodec='copy'
        )
    )

    @ffmpeg.on("progress")
    def on_progress(progress):
        percent = (progress.frame/frames_count)*100
        print(f"{proxy_file} : {int(percent)} %")

    ffmpeg.execute()

def concatenate_videos(temp_dir, videos, output_framerate=24):
    concat_txt_file = path_utils.join(temp_dir, 'concat.txt')
    with open(concat_txt_file, 'w') as file:
        for video in videos:
            proxy_video_file = path_utils.join(temp_dir, video)
            if not path_utils.isfile(proxy_video_file):
                logger.warning(f"{proxy_video_file} not found")
                continue
            file.write(f"file '{video}'\n")

    output_video_file = path_utils.join(temp_dir, 'concatened.mp4')
    if path_utils.isfile(output_video_file):
        path_utils.remove(output_video_file)

    command = [
        'ffmpeg',
        '-f', 'concat',
        '-safe', '0',
        '-i', concat_txt_file,
        '-c', 'copy',
        '-fflags', '+genpts',
        output_video_file
    ]

    subprocess.run(command)#, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
    return output_video_file

def get_frames_count(video_file):
    cap = cv2.VideoCapture(video_file)
    return cap.get(cv2.CAP_PROP_FRAME_COUNT)