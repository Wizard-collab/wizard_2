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
from PIL import Image, ImageFont, ImageDraw
import re

# Wizard modules
from wizard.core import assets
from wizard.core import project
from wizard.core import path_utils
from wizard.core import environment
from wizard.core import image
from wizard.core import tools
from wizard.core import ocio_utils

logger = logging.getLogger(__name__)


def add_video(variant_id, images_directory, frange, string_asset, focal_lengths_dic=None, comment='', analyse_comment=None, frame_rate=None, overlay=True):
    temp_video_file, to_thumbnail = merge_video(
        images_directory, frange, string_asset, focal_lengths_dic, frame_rate, overlay=overlay)
    if not temp_video_file:
        return
    video_id = assets.add_video(
        variant_id, comment=comment, analyse_comment=analyse_comment)
    video_row = project.get_video_data(video_id)
    video_path = video_row['file_path']
    thumbnail_path = video_row['thumbnail_path']
    logger.info(f"Copying video file to {video_path}")
    shutil.copyfile(temp_video_file, video_path)
    image.resize_preview(to_thumbnail, thumbnail_path)
    if path_utils.isfile(video_path):
        path_utils.rmtree(images_directory)
    return video_path


def request_video(variant_id):
    temp_video_dir = assets.get_temp_video_path(variant_id)
    path_utils.makedirs(temp_video_dir)
    logger.info(
        f"Temporary directory created : {temp_video_dir}, if something goes wrong in the video process please go there to find your temporary video file")
    return temp_video_dir


def merge_video(images_directory, frange, string_asset, focal_lengths_dic=None, frame_rate=None, overlay=True):
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

    if not frame_rate:
        frame_rate = project.get_frame_rate()
    img_array, size = merge_with_overlay(
        files_list, frange, frame_rate, string_asset, focal_lengths_dic, overlay=overlay)

    out = cv2.VideoWriter(
        temp_video_file, cv2.VideoWriter_fourcc(*"X264"), frame_rate, size)
    logger.info("Adding video overlay")
    for i in range(len(img_array)):
        out.write(img_array[i])
        if int(len(img_array)/2) == i:
            to_thumbnail = path_utils.join(images_directory, 'thumbnail.png')
            cv2.imwrite(to_thumbnail, img_array[i])
    logger.info("Writing video")
    out.release()

    if path_utils.isfile(temp_video_file):
        return temp_video_file, to_thumbnail


def merge_with_overlay(files_list, frange, frame_rate, string_asset, focal_lengths_dic=None, overlay=True):
    img_array = []
    for file in files_list:
        frame_number = frange[0] + files_list.index(file)
        focal_len = 'Focal not found'
        if focal_lengths_dic:
            if str(frame_number) in focal_lengths_dic.keys():
                focal_len = focal_lengths_dic[str(frame_number)]
        if overlay:
            pil_img = add_overlay(file, string_asset,
                                  frame_number, frange, frame_rate, focal_len)
        else:
            pil_img = Image.open(file)
        img = np.asarray(pil_img)
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    return img_array, size


def merge_only(files_list):
    img_array = []
    for file in files_list:
        img = cv2.imread(file)
        height, width, layers = img.shape
        size = (width, height)
        img_array.append(img)
    return img_array, size


def add_overlay(file, string_asset, frame_number, frange, frame_rate, focal_len):
    pil_image = Image.open(file)
    pil_image = pil_image.convert('RGBA')

    bg_image = Image.new('RGBA', pil_image.size, (70, 70, 70, 255))

    over_image = Image.new('RGBA', pil_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(over_image)
    # Draw overlay
    im_width, im_height = pil_image.size
    margin_percent = int((im_height*1)/100)
    font_size = int((im_width*1)/100)
    font = ImageFont.truetype('cour.ttf', font_size)
    # font_width, font_height = font.getsize(string_asset)
    font_width = font.getbbox(string_asset)[2]
    font_height = font.getbbox(string_asset)[3]
    rectangle_xy = [0, im_height -
                    (margin_percent*2+font_height), im_width, im_height]
    draw.rectangle(rectangle_xy, fill=(0, 0, 0, 120), outline=None)
    # Draw string asset
    string_asset_position = (
        margin_percent, im_height - (font_height + margin_percent))
    draw.text(string_asset_position, string_asset, font=font, fill="white")
    # Draw frame text
    frame_text = f"[{frange[0]}-{frange[1]}] - f{frame_number} - {frame_rate}fps - focal : {focal_len}"
    # font_width, font_height = font.getsize(frame_text)
    font_width = font.getbbox(frame_text)[2]
    font_height = font.getbbox(frame_text)[3]
    frame_text_position = (im_width/2 - font_width/2,
                           im_height - (font_height + margin_percent))
    draw.text(frame_text_position, frame_text, font=font, fill="white")
    # Draw user text
    user_text = environment.get_user()
    # font_width, font_height = font.getsize(user_text)
    font_width = font.getbbox(user_text)[2]
    font_height = font.getbbox(user_text)[3]
    user_text_position = (im_width - font_width - margin_percent,
                          im_height - (font_height + margin_percent))
    draw.text(user_text_position, user_text, font=font, fill="white")

    out = Image.alpha_composite(bg_image, pil_image)
    out = Image.alpha_composite(out, over_image)
    out = out.convert('RGB')
    return out


def video_from_render(export_version_id, ics, ocs, frame_rate, comment='', overlay=True):

    directory = assets.get_export_version_path(export_version_id)
    export_id = project.get_export_version_data(export_version_id, 'export_id')
    stage_id = project.get_export_data(export_id, 'stage_id')
    variant_id = project.get_stage_data(stage_id, 'default_variant_id')

    all_files = path_utils.listdir(directory)
    if len(all_files) == 0:
        logger.warning(f'No files found in {directory}')
        return

    files_dic = dict()
    for file in path_utils.listdir(directory):
        extension = path_utils.splitext(file)[-1].replace('.', '')
        if extension not in files_dic.keys():
            files_dic[extension] = []
        files_dic[extension].append(path_utils.join(directory, file))

    for extension in files_dic.keys():
        if extension in ['exr', 'png']:
            temp_dir = tools.temp_dir()
            ocio_utils.exr_to_png(files=files_dic[extension],
                                  output_dir=temp_dir,
                                  ics=ics,
                                  ocs=ocs)
            string_asset = assets.instance_to_string(
                ('export_version', export_version_id))

            frame_range = [find_frame_number(files_dic[extension][0]), find_frame_number(
                files_dic[extension][0])+len(files_dic[extension])-1]

            add_video(variant_id, temp_dir, frame_range, string_asset,
                      comment=comment, frame_rate=frame_rate, overlay=overlay)
            break


def find_frame_number(filename):
    # Regular expression to match "frame" followed by 3 to 5 digits, with optional underscore, hyphen, or dot
    match = re.search(r"[\._](\d+)\.(exr|png)$", filename)

    if match:
        # Return the frame number as an integer
        return int(match.group(1))
    else:
        # Return None if no valid frame number is found
        return 0
