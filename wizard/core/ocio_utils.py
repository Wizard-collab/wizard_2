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
This module provides utility functions for working with OpenColorIO (OCIO) and 
OpenEXR files, enabling color transformations and conversions between EXR and 
PNG image formats. It includes functions for:

- Converting EXR files to RGBA NumPy arrays.
- Saving NumPy arrays as PNG images.
- Applying color transformations using OCIO configurations.
- Retrieving available color spaces from an OCIO configuration.

The module is designed to integrate with the Wizard project and relies on 
external libraries such as PyOpenColorIO, OpenEXR, and NumPy.
"""

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
    """
    Save a given image represented as a NumPy array to a PNG file.

    This function takes a floating-point NumPy array representing an image,
    scales its values to the 0-255 range, converts it to an 8-bit unsigned
    integer format, and saves it as a PNG file using the RGBA color mode.

    Args:
        image_array (numpy.ndarray): A 2D or 3D NumPy array representing the image.
            The array values are expected to be in the range [0.0, 1.0].
        output_path (str): The file path where the PNG image will be saved.

    Raises:
        ValueError: If the input array is not in the expected format or range.
        IOError: If there is an error saving the image to the specified path.
    """
    # Convert the float array to uint8 (0-255) range
    image_array = (image_array * 255).astype(np.uint8)
    # Create a PIL image from the NumPy array
    image = Image.fromarray(image_array, mode='RGBA')
    # Save the image
    image.save(output_path)


def exr_to_rgba_array(file_path):
    """
    Converts an OpenEXR file to a 4-channel RGBA numpy array.
    Args:
        file_path (str): The file path to the OpenEXR file.
    Returns:
        numpy.ndarray: A 3D numpy array of shape (height, width, 4) containing 
        the RGBA data. Each channel (R, G, B, A) is represented as a float32 
        value. If the EXR file does not contain an alpha channel, the alpha 
        values will default to 1.0.
    Raises:
        OpenEXR.InputFileError: If the file cannot be opened or read.
        ValueError: If the EXR file contains invalid or corrupted data.
    Notes:
        - The function assumes the EXR file uses float32 pixel data.
        - The alpha channel is optional in the EXR file. If absent, the alpha 
          values are set to 1.0 by default.
    """
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
    """
    Converts a list of EXR files to PNG format while applying a color transformation
    using OpenColorIO (OCIO).
    Args:
        files (list of str): A list of file paths to the input EXR files.
        output_dir (str): The directory where the converted PNG files will be saved.
        ics (str): The input color space name.
        ocs (str): The output color space name.
        OCIO_config_file (str): Path to the OCIO configuration file. If not provided,
                                the current OCIO configuration will be used.
    Returns:
        int: Returns 1 on successful conversion of all files.
    Raises:
        Exception: If an error occurs during the color transformation or file processing.
    Notes:
        - This function uses OpenColorIO to perform the color transformation.
        - The `exr_to_rgba_array` function is expected to convert an EXR file to an RGBA array.
        - The `save_as_png` function is expected to save an RGBA array as a PNG file.
        - The `project.get_OCIO()` function is used to retrieve the OCIO configuration file
          if not explicitly provided.
    """
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
    """
    Converts a list of EXR image files to PNG format and saves them to the specified output directory.

    Args:
        files (list of str): A list of file paths to the EXR image files to be converted.
        output_dir (str): The directory where the converted PNG files will be saved.

    Returns:
        int: Returns 1 upon successful completion of the conversion process.

    Notes:
        - This function assumes the existence of helper functions `exr_to_rgba_array`, 
          `path_utils.join`, `path_utils.basename`, `path_utils.splitext`, and `save_as_png`.
        - The output PNG files will have the same base name as the input EXR files.
    """
    for file in files:
        img = exr_to_rgba_array(file)
        file_path = path_utils.join(
            output_dir, f"{path_utils.basename(path_utils.splitext(file)[0])}.png")
        save_as_png(img, file_path)
    return 1


def exr_to_png(files, output_dir, ics=None, ocs=None):
    """
    Converts a list of EXR files to PNG format, optionally applying a color 
    transformation using an OpenColorIO (OCIO) configuration.

    If an OCIO configuration file is available, the function applies a color 
    transformation from the input color space (ics) to the output color space (ocs). 
    Otherwise, it performs a direct conversion without color transformation.

    Args:
        files (list of str): A list of file paths to the EXR files to be converted.
        output_dir (str): The directory where the converted PNG files will be saved.
        ics (str, optional): The input color space for the color transformation. 
                             Defaults to None.
        ocs (str, optional): The output color space for the color transformation. 
                             Defaults to None.

    Returns:
        None
    """
    OCIO_config_file = project.get_OCIO()
    if not OCIO_config_file:
        return convert_exr_to_png(files, output_dir)
    return convert_exr_to_png_with_color_transform(files=files,
                                                   output_dir=output_dir,
                                                   ics=ics,
                                                   ocs=ocs,
                                                   OCIO_config_file=OCIO_config_file)


def get_OCIO_available_color_spaces():
    """
    Retrieves a list of available color spaces from the current or specified 
    OpenColorIO (OCIO) configuration.

    This function checks if a specific OCIO configuration file is provided 
    by the project. If so, it loads the configuration from that file. 
    Otherwise, it uses the current OCIO configuration. It then iterates 
    through the color spaces defined in the configuration and returns their names.

    Returns:
        list: A list of strings representing the names of available color spaces.
    """
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
