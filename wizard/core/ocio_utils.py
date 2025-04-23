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
import PyOpenColorIO as OCIO
import OpenEXR
import Imath
import os
import numpy as np
from PIL import Image

# Wizard core modules
from wizard.core import path_utils
from wizard.core import project


def save_as_png(image_array, output_path):
    # Convert the float array to uint8 (0-255) range
    image_array = (image_array * 255).astype(np.uint8)
    # Create a PIL image from the NumPy array
    image = Image.fromarray(image_array, mode='RGBA')
    # Save the image
    image.save(output_path)


def exr_to_rgba_array(file_path):
    # Open the EXR file
    exr_file = OpenEXR.InputFile(file_path)

    # Get the image size (resolution)
    header = exr_file.header()
    dw = header['dataWindow']
    width = dw.max.x - dw.min.x + 1
    height = dw.max.y - dw.min.y + 1

    # Define the channel type for R, G, B, and A (float)
    FLOAT = Imath.PixelType(Imath.PixelType.FLOAT)

    # Read the color channels from the EXR file
    r_channel = exr_file.channel('R', FLOAT)
    g_channel = exr_file.channel('G', FLOAT)
    b_channel = exr_file.channel('B', FLOAT)

    # Read alpha channel if it exists
    try:
        a_channel = exr_file.channel('A', FLOAT)
        has_alpha = True
    except:
        # Default alpha is 1.0 if absent
        a_channel = np.full((width * height), 1.0, dtype=np.float32)
        has_alpha = False

    # Convert the strings to numpy arrays and reshape them to 2D arrays
    r = np.frombuffer(r_channel, dtype=np.float32).reshape(height, width)
    g = np.frombuffer(g_channel, dtype=np.float32).reshape(height, width)
    b = np.frombuffer(b_channel, dtype=np.float32).reshape(height, width)
    a = np.frombuffer(a_channel, dtype=np.float32).reshape(
        height, width) if has_alpha else np.ones((height, width), dtype=np.float32)

    # Stack the channels into a single RGBA array
    rgba_array = np.stack([r, g, b, a], axis=-1)

    return rgba_array


def convert_exr_to_png_with_color_transform(files, output_dir, ics, ocs, OCIO_config_file):
    try:
        OCIO_config_file = project.get_OCIO()
        if OCIO_config_file:
            config = OCIO.Config.CreateFromFile(OCIO_config_file)
        else:
            config = OCIO.GetCurrentConfig()
        OCIO.SetCurrentConfig(config)
        processor = config.getProcessor(OCIO.ColorSpaceTransform(
            src=ics,
            dst=ocs
        ))
        cpu = processor.getDefaultCPUProcessor()

        # Apply the color transform to the existing RGBA pixel data
        for file in files:
            img = exr_to_rgba_array(file)
            cpu.applyRGBA(img)
            file_path = path_utils.join(
                output_dir, f"{path_utils.basename(path_utils.splitext(file)[0])}.png")
            save_as_png(img, file_path)
        return 1

    except Exception as e:
        print("OpenColorIO Error: ", e)


def convert_exr_to_png(files, output_dir):
    for file in files:
        img = exr_to_rgba_array(file)
        file_path = path_utils.join(
            output_dir, f"{path_utils.basename(path_utils.splitext(file)[0])}.png")
        save_as_png(img, file_path)
    return 1


def exr_to_png(files, output_dir, ics=None, ocs=None):
    OCIO_config_file = project.get_OCIO()
    if not OCIO_config_file:
        return convert_exr_to_png(files, output_dir)
    return convert_exr_to_png_with_color_transform(files=files,
                                                   output_dir=output_dir,
                                                   ics=ics,
                                                   ocs=ocs,
                                                   OCIO_config_file=OCIO_config_file)


def get_OCIO_available_color_spaces():
    available_color_spaces = []
    OCIO_config_file = project.get_OCIO()
    if OCIO_config_file:
        config = OCIO.Config.CreateFromFile(OCIO_config_file)
    else:
        config = OCIO.GetCurrentConfig()
    OCIO.SetCurrentConfig(config)
    for cs in config.getColorSpaces():
        available_color_spaces.append(cs.getName())
    return available_color_spaces
