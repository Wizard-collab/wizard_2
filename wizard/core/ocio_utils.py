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

import logging 
logger = logging.getLogger(__name__)


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

def _find_channel_name(header_channels, short_name):
        short = short_name.lower()
        for name in header_channels.keys():
            try:
                if name.split('.')[-1].lower() == short:
                    return name
            except Exception:
                # fallback to direct comparison
                if name.lower() == short:
                    return name
        return None

def exr_to_rgba_array(file_path, channel=None):
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

    header_channels = header['channels']

    # Find actual channel names for R, G, B based on channel parameter
    if channel:
        # Special handling for basic RGB/RGBA channel groups
        if channel in ['RGB', 'RGBA']:
            # For basic channel groups, look for direct R, G, B, A channels
            r_name = 'R' if 'R' in header_channels else ('r' if 'r' in header_channels else None)
            g_name = 'G' if 'G' in header_channels else ('g' if 'g' in header_channels else None)
            b_name = 'B' if 'B' in header_channels else ('b' if 'b' in header_channels else None)
            a_name = 'A' if 'A' in header_channels else ('a' if 'a' in header_channels else None)
        else:
            # If channel is specified, look for RGB channels with that prefix (case-insensitive)
            r_name = None
            g_name = None
            b_name = None
            a_name = None
            
            # Check both uppercase and lowercase variants
            for suffix_upper, suffix_lower in [('R', 'r'), ('G', 'g'), ('B', 'b'), ('A', 'a')]:
                channel_upper = f"{channel}.{suffix_upper}"
                channel_lower = f"{channel}.{suffix_lower}"
                
                if suffix_upper == 'R':
                    r_name = channel_upper if channel_upper in header_channels else (channel_lower if channel_lower in header_channels else None)
                elif suffix_upper == 'G':
                    g_name = channel_upper if channel_upper in header_channels else (channel_lower if channel_lower in header_channels else None)
                elif suffix_upper == 'B':
                    b_name = channel_upper if channel_upper in header_channels else (channel_lower if channel_lower in header_channels else None)
                elif suffix_upper == 'A':
                    a_name = channel_upper if channel_upper in header_channels else (channel_lower if channel_lower in header_channels else None)
    else:
        # Default behavior: find any R, G, B channels using the helper
        r_name = _find_channel_name(header_channels, 'R')
        g_name = _find_channel_name(header_channels, 'G')
        b_name = _find_channel_name(header_channels, 'B')
        a_name = _find_channel_name(header_channels, 'A')

    if not (r_name and g_name and b_name):
        available = list(header_channels.keys())
        if channel:
            raise ValueError(
                "Could not find R/G/B channels for '{}' in EXR header. Available channels: {}".format(channel, available)
            )
        else:
            raise ValueError(
                "Could not find R/G/B channels in EXR header. Available channels: {}".format(available)
            )

    # Read the found channels
    r_channel = exr_file.channel(r_name, FLOAT)
    g_channel = exr_file.channel(g_name, FLOAT)
    b_channel = exr_file.channel(b_name, FLOAT)

    # Read alpha channel if it exists
    if a_name:
        a_channel = exr_file.channel(a_name, FLOAT)
        has_alpha = True
    else:
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

def list_exr_channels(file_path):
    """
    Lists all available channels in an OpenEXR file.
    
    Args:
        file_path (str): Path to the EXR file
        
    Returns:
        list: List of channel names available in the EXR file
    """
    try:
        exr_file = OpenEXR.InputFile(file_path)
        header = exr_file.header()
        channels = header['channels']
        return list(channels.keys())
    except Exception as e:
        print(f"Error reading EXR file: {e}")
        return []


def get_exr_channel_groups(file_path):
    """
    Gets unique channel group prefixes by removing common color suffixes (.R, .G, .B, .A).
    
    For example:
    - 'ViewLayer.Combined.R', 'ViewLayer.Combined.G', 'ViewLayer.Combined.B' -> 'ViewLayer.Combined'
    - 'layer.R', 'layer.G', 'layer.B' -> 'layer'
    - 'R', 'G', 'B', 'A' -> 'RGBA' (basic channels group with alpha)
    - 'R', 'G', 'B' -> 'RGB' (basic channels group without alpha)
    - 'Depth' -> 'Depth' (no suffix to remove)
    
    Args:
        file_path (str): Path to the EXR file
        
    Returns:
        list: List of unique channel group prefixes (base layer names)
    """
    try:
        channels = list_exr_channels(file_path)
        if not channels:
            return []
        
        # Color channel suffixes to remove (both uppercase and lowercase)
        color_suffixes = ['.R', '.G', '.B', '.A', '.r', '.g', '.b', '.a']
        basic_color_channels = {'R', 'G', 'B', 'A', 'r', 'g', 'b', 'a'}
        
        groups = set()
        basic_channels_found = set()
        
        for channel in channels:
            # Check if this is a basic color channel (R, G, B, A without prefix)
            if channel in basic_color_channels:
                basic_channels_found.add(channel.upper())
                continue
            
            # Check if channel ends with a color suffix
            base_name = channel
            for suffix in color_suffixes:
                if channel.endswith(suffix):
                    base_name = channel[:-len(suffix)]
                    break
            groups.add(base_name)
        
        # If we found basic R, G, B (and optionally A) channels, add them as a group
        if basic_channels_found:
            # Check if we have at least R, G, B
            if {'R', 'G', 'B'}.issubset(basic_channels_found):
                # Use 'RGBA' if alpha is present, otherwise 'RGB'
                if 'A' in basic_channels_found:
                    groups.add('RGBA')
                else:
                    groups.add('RGB')
        
        return sorted(list(groups))
    
    except Exception as e:
        print(f"Error reading EXR channel groups: {e}")
        return []

def convert_exr_to_png_with_color_transform(files, output_dir, ics, ocs, channel, OCIO_config_file):
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
            img = exr_to_rgba_array(file, channel=channel)
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
        logger.info(f"Converting EXR to PNG: {file}")
        img = exr_to_rgba_array(file)
        file_path = path_utils.join(
            output_dir, f"{path_utils.basename(path_utils.splitext(file)[0])}.png")
        save_as_png(img, file_path)
    return 1


def exr_to_png(files, output_dir, ics=None, ocs=None, channel=None):
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
                                                   channel=channel,
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
