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
import os
import logging
import cv2
import numpy as np
import shutil

# Wizard modules
from wizard.core import assets
from wizard.core import project
from wizard.core import path_utils
from wizard.core import image

logger = logging.getLogger(__name__)

def add_video(work_env_id, images_directory, comment=''):
    temp_video_file, to_thumbnail = merge_video(images_directory)
    if not temp_video_file:
        return
    video_id = assets.add_video(work_env_id)
    video_row = project.get_video_data(video_id)
    video_path = video_row['file_path']
    thumbnail_path = video_row['thumbnail_path']
    logger.info(f"Copying video file to {video_path}")
    shutil.copyfile(temp_video_file, video_path)
    image.resize_preview(to_thumbnail, thumbnail_path)
    if path_utils.isfile(video_path):
        path_utils.rmtree(images_directory)
    print('lol')
    return video_path

def request_video(work_env_id):
    temp_video_dir = assets.get_temp_video_path(work_env_id)
    path_utils.makedirs(temp_video_dir)
    return temp_video_dir

def merge_video(images_directory):
    temp_video_file = path_utils.join(images_directory, "temp.mp4")

    files_list = []
    if not path_utils.isdir(images_directory):
        logger.warning(f"{images_directory} not found, can't create video")
        return
    for image_file in path_utils.listdir(images_directory):
        if image_file.endswith('.png'):
            files_list.append(path_utils.join(images_directory, image_file))
    if files_list == []:
        logger.warning(f"{images_directory} is empty, can't create video.")
        return
    img_array = []
    for file in files_list:
        img = cv2.imread(file)
        height, width, layers = img.shape
        size = (width,height)
        img_array.append(img)

    frame_rate = project.get_frame_rate()

    out = cv2.VideoWriter(temp_video_file,cv2.VideoWriter_fourcc(*'MP4V'), frame_rate, size)
    for i in range(len(img_array)):
        out.write(img_array[i])
    out.release()

    to_thumbnail = files_list[int(len(files_list)/2)]

    if path_utils.isfile(temp_video_file):
        return temp_video_file, to_thumbnail
