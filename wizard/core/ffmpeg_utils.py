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
This module provides utility functions for working with video files using FFmpeg and OpenCV.

The functions include:
- Merging multiple video files into a single video.
- Extracting the first frame of a video.
- Getting the total frame count of a video.
- Constructing file paths for temporary and concatenated video files.
- Concatenating video segments with specified in/out points.

These utilities are designed to support the 'wizard' application's video management features.
"""

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
    """
    Merges multiple video files into a single video file using FFmpeg.

    This function creates a temporary text file listing the input video files,
    then uses FFmpeg to concatenate them into a single output file. The
    temporary file is deleted after the operation is complete.

    Args:
        input_files (list of str): A list of file paths to the input video files
            to be merged. The files should be in a format that supports
            concatenation without re-encoding.
        output_file (str): The file path where the merged video will be saved.

    Raises:
        ffmpeg.Error: If an error occurs during the FFmpeg operation, it will
            be logged, and the exception will be raised.

    Side Effects:
        - Creates a temporary text file in the system's temporary directory.
        - Deletes the temporary file after the operation is complete.
        - Logs information and errors using the `logger` object.

    Example:
        merge_videos(['video1.mp4', 'video2.mp4'], 'output.mp4')
    """
    # Create a temporary file to list the input video files
    temp_file = path_utils.join(tools.temp_dir(), 'concat_files.txt')
    with open(temp_file, 'w') as file_list:
        # Write each input file path to the temporary file
        for input_file in input_files:
            file_list.write(f"file '{input_file}'\n")

    try:
        # Use FFmpeg to merge the video files listed in the temporary file
        (
            ffmpeg
            # Specify input as a concatenation list
            .input(temp_file, format='concat', safe=0)
            .output(output_file, c='copy')  # Copy codec without re-encoding
            # Overwrite the output file if it exists
            .run(overwrite_output=True)
        )
        # Log success message
        logger.info(f"Merged video saved as {output_file}")
    except ffmpeg.Error as e:
        # Log error message if FFmpeg fails
        logger.error(
            f"Error occurred while merging videos: {e.stderr.decode('utf8')}")
    finally:
        # Remove the temporary file after the operation
        os.remove(temp_file)


def get_temp_dir():
    """
    Returns the path to a temporary directory specifically used for the 
    'wizard' application's video manager. If the directory does not exist, 
    it is created.

    The temporary directory is located within the system's temporary 
    directory and follows the structure: <tempdir>/wizard/video_manager.

    Returns:
        str: The absolute path to the temporary directory.
    """
    tmp_dir = path_utils.join(tempfile.gettempdir(), 'wizard', 'video_manager')
    if not path_utils.isdir(tmp_dir):
        path_utils.makedirs(tmp_dir)
    return tmp_dir


def get_frames_count(video_file):
    """
    Get the total number of frames in a video file.

    Args:
        video_file (str): The path to the video file.

    Returns:
        float: The total number of frames in the video. Returns 0 if the video
        file cannot be opened or the frame count cannot be determined.
    """
    cap = cv2.VideoCapture(video_file)
    return cap.get(cv2.CAP_PROP_FRAME_COUNT)


def extract_first_frame(video_file, temp_dir):
    """
    Extracts the first frame of a video file and saves it as a PNG image.

    Args:
        video_file (str): The path to the video file from which the frame will be extracted.
        temp_dir (str): The directory where the extracted frame will be saved.

    Returns:
        str: The full path to the saved PNG image.

    Note:
        - The function captures the first frame of the video and saves it as a PNG file
          in the specified temporary directory.
        - The output file is named using the base name of the video file with a `.png` extension.
    """
    cap = cv2.VideoCapture(video_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(cap.get(cv2.CAP_PROP_FRAME_COUNT)/2))
    ret, frame = cap.read()
    destination_file = path_utils.join(
        temp_dir, f"{path_utils.basename(video_file)}.png")
    cv2.imwrite(destination_file, frame)
    return destination_file


def get_concat_video_file(temp_dir, player_id):
    """
    Constructs the file path for a concatenated video file.

    Args:
        temp_dir (str): The directory where the temporary video file is stored.
        player_id (str): The identifier for the player, used to name the video file.

    Returns:
        str: The full file path of the concatenated video file, named as '{player_id}.mp4'.
    """
    return path_utils.join(temp_dir, f'{player_id}.mp4')


def concatenate_videos(temp_dir, player_id, videos_dic, fps=24):
    """
    Concatenates multiple video files into a single video using FFmpeg.

    Args:
        temp_dir (str): The temporary directory where intermediate files will be stored.
        player_id (str): A unique identifier for the player, used to name intermediate and output files.
        videos_dic (dict): A dictionary containing video metadata. Each key represents a video, and the value is a 
            dictionary with the following keys:
                - 'original_file' (str): The path to the original video file.
                - 'inpoint' (float): The starting point (in frames) of the video segment to include.
                - 'outpoint' (float): The ending point (in frames) of the video segment to include.
        fps (int, optional): The frame rate of the output video. Defaults to 24.

    Returns:
        str: The path to the concatenated output video file, or None if no files were provided for concatenation.

    Raises:
        subprocess.SubprocessError: If the FFmpeg command fails during execution.

    Notes:
        - This function generates a temporary text file listing the video files and their in/out points for FFmpeg.
        - The FFmpeg command is executed with the `-f concat` option to concatenate the videos.
        - The output video is created without audio (`-an`) and uses the `-preset ultrafast` setting for speed.
    """
    # Create a temporary text file to list the video files and their in/out points
    concat_txt_file = path_utils.join(temp_dir, f'{player_id}.txt')
    files = []
    with open(concat_txt_file, 'w') as file:
        # Write each video's file path and in/out points to the text file
        for video in videos_dic.keys():
            file.write(f"file '{videos_dic[video]['original_file']}'\n")
            file.write(f"inpoint {videos_dic[video]['inpoint']/fps}\n")
            file.write(f"outpoint {videos_dic[video]['outpoint']/fps}\n")
            files.append(videos_dic[video]['original_file'])

    # If no files are provided, log a debug message and return
    if len(files) == 0:
        logger.debug("No files to concat.")
        return

    # Construct the output video file path
    output_video_file = get_concat_video_file(temp_dir, player_id)

    # Build the FFmpeg command to concatenate the videos
    command = f"ffmpeg -y -f concat -safe 0 -i {concat_txt_file} -preset ultrafast -c copy -an -r {fps} {output_video_file}"

    # Execute the FFmpeg command and capture the output
    res = subprocess.run(command, stderr=subprocess.PIPE,
                         stdout=subprocess.PIPE)

    # Return the path to the concatenated video file
    return output_video_file
