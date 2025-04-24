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
This module provides a collection of utility functions for image processing and manipulation.
It includes functionalities such as resizing, cropping, converting images to different formats,
generating random images, and handling screenshots. The module leverages the Pillow library
for image manipulation and PyQt6 for capturing screenshots.

Key functionalities:
- Screenshot capturing and thumbnail generation.
- Image resizing and cropping while maintaining aspect ratios.
- Conversion between different image formats (e.g., bytes, strings, PIL images).
- Random image generation with customizable text and background colors.
- Handling ICC profiles for color management.

Dependencies:
- PyQt6
- Pillow (PIL)
- Wizard modules (tools, path_utils)
"""

# Python modules
from PyQt6 import QtGui, QtCore
from PIL import Image, ImageCms, ImageFont, ImageDraw
import io
import base64
import random
import colorsys
import os

# Wizard modules
from wizard.core import tools
from wizard.core import path_utils


def screenshot(file, thumbnail_file):
    """
    Captures a screenshot of the current screen, resizes it, and saves both the 
    full-sized image and a thumbnail version to the specified file paths.
    Args:
        file (str): The file path where the full-sized screenshot will be saved.
        thumbnail_file (str): The file path where the thumbnail image will be saved.
    Returns:
        tuple: A tuple containing the paths of the saved full-sized image and thumbnail image.
    Notes:
        - The full-sized image is resized to a maximum width of 1000 pixels while maintaining aspect ratio.
        - The thumbnail image is resized to a fixed width of 200 pixels while maintaining aspect ratio.
        - The images are saved in PNG and JPEG formats respectively.
    """
    # Get the screen where the cursor is currently located
    screen = QtGui.QGuiApplication.screenAt(QtGui.QCursor().pos())

    # Get the available geometry of the screen (position and size)
    rect = screen.availableGeometry()
    x = rect.x()
    y = rect.y()
    width = rect.width()
    height = rect.height()

    # Capture a screenshot of the entire screen
    pixmap = screen.grabWindow(
        0, x=x, y=y, width=width, height=height
    )

    # Convert the captured pixmap to a PIL image
    base_image = pixmap_to_PIL(pixmap)

    # Resize the base image to a maximum width of 1000 pixels while maintaining aspect ratio
    image = resize_image(base_image, 1000)

    # Create a thumbnail by resizing the base image to a fixed width of 200 pixels
    thumbnail, null, null = resize_image_with_fixed_width(base_image, 200)

    # Generate a unique file name for the full-sized image
    save_file = tools.get_filename_without_override(file)

    # Generate a unique file name for the thumbnail image
    save_thumbnail_file = tools.get_filename_without_override(thumbnail_file)

    # Save the full-sized image in PNG format
    image.save(save_file, format="PNG")

    # Save the thumbnail image in JPEG format
    thumbnail.save(save_thumbnail_file, format="JPEG")

    # Return the file paths of the saved full-sized image and thumbnail
    return save_file, save_thumbnail_file


def pixmap_to_PIL(pixmap):
    """
    Converts a QPixmap object to a PIL.Image object.

    This function takes a QPixmap, saves it to an in-memory buffer in PNG format,
    and then reads the buffer to create and return a PIL.Image object.

    Args:
        pixmap (QtGui.QPixmap): The QPixmap object to be converted.

    Returns:
        PIL.Image.Image: The resulting PIL.Image object.
    """
    buffer = QtCore.QBuffer()
    buffer.open(QtCore.QIODevice.OpenModeFlag.ReadWrite)
    pixmap.save(buffer, "PNG")
    PIL_image = Image.open(io.BytesIO(buffer.data()))
    return PIL_image


def resize_preview(file, destination, size=200, image_format="PNG"):
    """
    Resizes an image to a fixed width and saves it as a preview file.

    Args:
        file (str): The path to the input image file.
        destination (str): The directory where the resized preview image will be saved.
        size (int, optional): The fixed width for resizing the image. Defaults to 200.
        image_format (str, optional): The format to save the preview image in. Defaults to "PNG".

    Returns:
        str: The path to the saved preview file, or None if the input file does not exist.

    Notes:
        - The function checks if the input file exists before proceeding.
        - The resized image is saved with a unique filename to avoid overwriting existing files.
    """
    if not path_utils.isfile(file):
        return
    image = Image.open(file)
    preview, null, null = resize_image_with_fixed_width(image, size)
    preview_file = tools.get_filename_without_override(destination)
    preview.save(preview_file, format=image_format)
    return preview_file


def convert_image_to_bytes(image_file, resize=None):
    """
    Converts an image file to its byte representation.

    This function opens the provided image file, optionally resizes it, 
    and returns the image data in PNG byte format.

    Args:
        image_file (str or file-like object): The path to the image file or a file-like object.
        resize (tuple, optional): A tuple (width, height) specifying the new size of the image. 
                                  If None, the image is not resized.

    Returns:
        bytes: The byte representation of the image in PNG format.

    Raises:
        IOError: If the image file cannot be opened or processed.
    """
    # Resize the given file to 100*100
    # and return the png bytes
    image = Image.open(image_file)
    return convert_PILLOW_image_to_bytes(image, resize)


def convert_PILLOW_image_to_bytes(image, resize=None):
    """
    Converts a PIL (Pillow) image to a byte array, optionally resizing it and 
    converting its color profile to sRGB if an ICC profile is present.

    Args:
        image (PIL.Image.Image): The input Pillow image to be converted.
        resize (tuple, optional): A tuple (width, height) specifying the new size 
            to resize the image to. If None, no resizing is performed.

    Returns:
        bytes: The image data in PNG format as a byte array.

    Notes:
        - If the image contains an ICC profile, it will be converted to the sRGB 
          color profile before saving.
        - The output image is always saved in PNG format.
    """
    # If a resize dimension is provided, resize the image
    if resize is not None:
        image = resize_image(image, resize)

    # Retrieve the ICC profile from the image metadata, if available
    icc = image.info.get("icc_profile", "")
    if icc:
        # Convert the ICC profile to an in-memory byte stream
        icc_io_handle = io.BytesIO(icc)

        # Create a source color profile from the ICC data
        src_profile = ImageCms.ImageCmsProfile(icc_io_handle)

        # Create a destination color profile for sRGB
        dst_profile = ImageCms.createProfile("sRGB")

        # Convert the image's color profile to sRGB
        image = ImageCms.profileToProfile(image, src_profile, dst_profile)

    # Create an in-memory byte stream to save the image
    stream = io.BytesIO()

    # Save the image in PNG format to the byte stream
    image.save(stream, format="PNG")

    # Retrieve the byte data from the stream
    imagebytes = stream.getvalue()

    # Return the byte representation of the image
    return imagebytes


def convert_image_bytes_to_pillow(image_bytes):
    """
    Converts image data in bytes format to a Pillow Image object.

    Args:
        image_bytes (bytes): The image data in bytes.

    Returns:
        PIL.Image.Image: A Pillow Image object created from the provided bytes.

    Raises:
        IOError: If the image data cannot be opened or is invalid.
    """
    image = Image.open(io.BytesIO(image_bytes))
    return image


def convert_screenshot(image_file, resize=300):
    """
    Converts an image file into a resized PNG image and returns its byte representation along with dimensions.

    Args:
        image_file (str or file-like object): The path to the image file or a file-like object to be processed.
        resize (int, optional): The fixed width to resize the image to. Defaults to 300.

    Returns:
        tuple: A tuple containing:
            - imagebytes (bytes): The byte representation of the resized PNG image.
            - width (int): The width of the resized image.
            - height (int): The height of the resized image.
    """
    image = Image.open(image_file)
    image, width, height = resize_image_with_fixed_width(image, resize)
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    imagebytes = stream.getvalue()
    return imagebytes, width, height


def convert_image_to_str_data(image_file, resize=None):
    """
    Converts an image file to a string representation of its data.

    This function takes an image file, optionally resizes it, and converts it 
    into a string representation of its binary data.

    Args:
        image_file (str or file-like object): The path to the image file or a file-like object.
        resize (tuple, optional): A tuple (width, height) specifying the dimensions to resize 
            the image to. If None, the image is not resized.

    Returns:
        str: A string representation of the image's binary data.
    """
    image_bytes = convert_image_to_bytes(image_file, resize)
    return convert_bytes_to_str_data(image_bytes)


def convert_bytes_to_str_data(image_bytes):
    """
    Converts a bytes object representing image data into a Base64-encoded ASCII string.

    Args:
        image_bytes (bytes): The image data in bytes format.

    Returns:
        str: The Base64-encoded ASCII string representation of the image data.
    """
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return encoded


def convert_str_data_to_image_bytes(str_data):
    """
    Decodes a Base64-encoded string into its corresponding binary image data.

    Args:
        str_data (str): A Base64-encoded string representing image data.

    Returns:
        bytes: The decoded binary image data.

    Raises:
        binascii.Error: If the input string is not properly Base64-encoded.
    """
    return base64.b64decode(str_data)


def resize_image(image, fixed_height):
    """
    Resizes a PIL (Pillow) image to a specified fixed height while maintaining the aspect ratio.

    Args:
        image (PIL.Image.Image): The input Pillow image to be resized.
        fixed_height (int): The desired height for the resized image.

    Returns:
        PIL.Image.Image: The resized image with the specified height and adjusted width 
                         to maintain the original aspect ratio.

    Notes:
        - The width of the image is calculated proportionally based on the fixed height.
        - The resizing is performed using the LANCZOS filter for high-quality downsampling.
    """
    height_percent = fixed_height / float(image.size[1])
    width_size = int((float(image.size[0]) * float(height_percent)))
    image = image.resize((width_size, fixed_height), Image.Resampling.LANCZOS)
    return image


def resize_image_file(image_file, fixed_height):
    """
    Resizes an image file to a specified height while maintaining aspect ratio.
    If the file is an SVG, the function does nothing.

    Args:
        image_file (str): The path to the image file to be resized.
        fixed_height (int): The desired height of the resized image in pixels.

    Returns:
        None: The function modifies the image file in place, saving it as a PNG.
    """
    if image_file.endswith(".svg"):
        return
    image = Image.open(image_file)
    image = resize_image(image, fixed_height)
    image.save(image_file, format="PNG")


def crop_image_height(pillow_image, height):
    """
    Crops the given Pillow image to the specified height.

    Args:
        pillow_image (PIL.Image.Image): The Pillow image to be cropped.
        height (int): The height to which the image should be cropped. 
                      The cropping starts from the top (0, 0) and extends 
                      to the specified height.

    Returns:
        PIL.Image.Image: The cropped image.
    """
    area = (0, 0, pillow_image.size[0], height)
    cropped_img = pillow_image.crop(area)
    return cropped_img


def resize_image_with_fixed_width(image, fixed_width):
    """
    Resize an image to a fixed width while maintaining its aspect ratio.

    Args:
        image (PIL.Image.Image): The input image to be resized.
        fixed_width (int): The desired fixed width for the resized image.

    Returns:
        tuple: A tuple containing:
            - PIL.Image.Image: The resized image.
            - int: The fixed width of the resized image.
            - int: The calculated height of the resized image.
    """
    width_percent = fixed_width / float(image.size[0])
    height_size = int((float(image.size[1]) * float(width_percent)))
    image = image.resize((fixed_width, height_size), Image.Resampling.LANCZOS)
    return image, fixed_width, height_size


def project_random_image(project_name):
    """
    Generates a random project image with a colored background, concentric circles, 
    and the first letter of the project name displayed in the center.
    Args:
        project_name (str): The name of the project. The first letter of this name 
                            will be used as the central text in the image.
    Returns:
        str: The file path to the generated image.
    The function creates an image with the following characteristics:
    - The background color is determined by a random hue, saturation, and value (HSV) 
      converted to RGB.
    - Three concentric circles are drawn with slightly lighter shades of the background color.
    - The first letter of the project name is displayed in white at the center of the image.
    - The image is saved as a temporary file and its path is returned.
    """
    # Extract the first letter of the project name and convert it to uppercase
    letter = project_name[0].upper()

    # Generate a random background color using HSV values
    hue = random.randint(0, 100) / 100.0
    saturation = random.randint(10, 50) / 100.0
    value = random.randint(30, 60) / 100.0
    rgb_tuple = tuple(
        round(i * 255) for i in colorsys.hsv_to_rgb(hue, saturation, value)
    )

    # Create a new image with the generated background color
    img = Image.new("RGB", (500, 282), color=rgb_tuple)

    # Initialize the drawing context for the image
    draw = ImageDraw.Draw(img)

    # Draw the outermost circle with a slightly lighter shade of the background color
    circle_rgb_tuple = tuple(
        round(i * 255) for i in colorsys.hsv_to_rgb(hue, saturation, value + 0.04)
    )
    draw.ellipse(
        ((500 - 500) / 2, (282 - 500) / 2, (500 + 500) / 2, (282 + 500) / 2),
        fill=circle_rgb_tuple,
        width=0,
    )

    # Draw the middle circle with an even lighter shade
    circle_rgb_tuple = tuple(
        round(i * 255) for i in colorsys.hsv_to_rgb(hue, saturation, value + 0.08)
    )
    draw.ellipse(
        ((500 - 350) / 2, (282 - 350) / 2, (500 + 350) / 2, (282 + 350) / 2),
        fill=circle_rgb_tuple,
        width=0,
    )

    # Draw the innermost circle with the lightest shade
    circle_rgb_tuple = tuple(
        round(i * 255) for i in colorsys.hsv_to_rgb(hue, saturation, value + 0.12)
    )
    draw.ellipse(
        ((500 - 200) / 2, (282 - 200) / 2, (500 + 200) / 2, (282 + 200) / 2),
        fill=circle_rgb_tuple,
        width=0,
    )

    # Load the font and calculate the size of the letter to be drawn
    font = ImageFont.truetype("ressources/fonts/Poppins-Black.ttf", 100)
    size = font.getbbox(letter)
    w, h = size[2], size[3]

    # Draw the letter in white at the center of the image
    draw.text(((500 - w) / 2, (282 - h - 30) / 2),
              letter, (255, 255, 255), font=font)

    # Save the generated image to a temporary file and return its path
    img_file = path_utils.join(tools.temp_dir(), "temp_img.png")
    img.save(img_file)
    return img_file


def user_random_image(user_name):
    """
    Generates a random image with a colored background and the first letter of the given user name.
    The background color is determined by a random hue, saturation, and value (HSV) converted to RGB.
    The first letter of the user name is displayed in white, centered on the image.
    Args:
        user_name (str): The name of the user. The first letter of this name will be used in the image.
    Returns:
        str: The file path to the generated image.
    """
    # Extract the first letter of the user name and convert it to uppercase
    letter = user_name[0].upper()

    # Generate a random background color using HSV values
    hue = random.randint(0, 100) / 100.0
    saturation = random.randint(10, 50) / 100.0
    value = random.randint(30, 60) / 100.0
    rgb_tuple = tuple(
        round(i * 255) for i in colorsys.hsv_to_rgb(hue, saturation, value)
    )

    # Create a new image with the generated background color
    img = Image.new("RGB", (100, 100), color=rgb_tuple)

    # Initialize the drawing context for the image
    draw = ImageDraw.Draw(img)

    # Load the font and calculate the size of the letter to be drawn
    font = ImageFont.truetype("ressources/fonts/Poppins-Black.ttf", 40)
    size = font.getbbox(letter)
    w, h = size[2], size[3]

    # Draw the letter in white at the center of the image
    draw.text(((100 - w) / 2, (100 - h - 10) / 2),
              letter, (255, 255, 255), font=font)

    # Save the generated image to a temporary file and return its path
    img_file = path_utils.join(tools.temp_dir(), "temp_img.png")
    img.save(img_file)
    return img_file
