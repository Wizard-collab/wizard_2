# coding: utf-8
# Author: Leo BRUNEL
# Contact: contact@leobrunel.com

# This module is used to manage images in wizard

# Python modules
import pyautogui
from PIL import Image, ImageCms
import io
import base64
import json

# Wizard modules
from wizard.core import tools

def screenshot(file, thumbnail_file):
    # Capture the screen
    # Divide the image size by ≈3
    base_image = pyautogui.screenshot()
    image = resize_image(base_image, 1000)

    thumbnail, null, null = resize_image_with_fixed_width(base_image, 200)

    save_file = tools.get_filename_without_override(file)
    save_thumbnail_file = tools.get_filename_without_override(thumbnail_file)

    image.save(save_file, format="PNG")
    thumbnail.save(save_thumbnail_file, format="JPEG")
    return save_file, save_thumbnail_file

def convert_image_to_bytes(image_file, resize=100):
    # Resize the given file to 100*100
    # and return the png bytes
    image = Image.open(image_file)
    image = resize_image(image, resize)

    icc = image.info.get('icc_profile', '')
    if icc:
        icc_io_handle = io.BytesIO(icc)
        src_profile = ImageCms.ImageCmsProfile(icc_io_handle)
        dst_profile = ImageCms.createProfile('sRGB')
        image = ImageCms.profileToProfile(image, src_profile, dst_profile)

    stream = io.BytesIO()
    image.save(stream, format="PNG")
    imagebytes = stream.getvalue()
    return imagebytes

def convert_screenshot(image_file, resize=300):
    # Resize the given file to 100*100
    # and return the png bytes
    image = Image.open(image_file)
    image, width, height = resize_image_with_fixed_width(image, resize)
    stream = io.BytesIO()
    image.save(stream, format="PNG")
    imagebytes = stream.getvalue()
    return imagebytes, width, height

def convert_image_to_str_data(image_file, resize=100):
    encoded = base64.b64encode(convert_image_to_bytes(image_file, resize)).decode('ascii')
    return encoded

def convert_str_data_to_image_bytes(str_data):
    return base64.b64decode(str_data)

def resize_image(image, fixed_height):
    height_percent = (fixed_height / float(image.size[1]))
    width_size = int((float(image.size[0]) * float(height_percent)))
    image = image.resize((width_size, fixed_height), Image.ANTIALIAS)
    return image

def resize_image_with_fixed_width(image, fixed_width):
    width_percent = (fixed_width / float(image.size[0]))
    height_size = int((float(image.size[1]) * float(width_percent)))
    image = image.resize((fixed_width, height_size), Image.ANTIALIAS)
    return image, fixed_width, height_size
    